from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import ManualBookmarkSerializer
from operations.models import Video, VideoLike
from users.models import Bookmark
from operations.serializers import UserPublicSerializer
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Create your views here.

def generate_tags_from_title(title):
    if not title:
        return []
    
    stop_words = set(stopwords.words('english'))
    # Add custom words to ignore
    stop_words.update(['video', 'hd', 'fhd', '4k', '1080p', '720p'])

    # Tokenize and filter out stop words and short words
    tokens = word_tokenize(title.lower())
    filtered_tokens = [
        word for word in tokens 
        if word.isalpha() and word not in stop_words and len(word) > 2
    ]

    # Part-of-speech tagging to find nouns
    tagged_tokens = nltk.pos_tag(filtered_tokens)
    
    # Extract nouns (NN, NNS, NNP, NNPS) as they are often the most relevant keywords
    keywords = [word for word, tag in tagged_tokens if tag in ('NN', 'NNS', 'NNP', 'NNPS')]
    
    return list(set(keywords)) # Return unique keywords

class URLMetadataScraperView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        url = request.data.get('url')
        if not url:
            return Response({"error": "URL is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': url 
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # --- Metadata Extraction ---
            title = soup.find('meta', property='og:title')
            description = soup.find('meta', property='og:description')
            thumbnail_url = soup.find('meta', property='og:image')
            
            # --- Embed URL Extraction (Multi-strategy) ---
            found_urls = set()

            # Strategy 1: Look for Open Graph video tags
            og_video = soup.find('meta', property='og:video:url') or soup.find('meta', property='og:video')
            if og_video and og_video.get('content'):
                found_urls.add(og_video['content'])

            # Strategy 2: Site-specific heuristics (YouTube, etc.)
            if 'youtube.com/watch?v=' in url:
                try:
                    video_id = url.split('v=')[1].split('&')[0]
                    found_urls.add(f'https://www.youtube.com/embed/{video_id}')
                except IndexError: pass
            elif 'vimeo.com/' in url:
                try:
                    video_id = url.split('/')[-1]
                    found_urls.add(f'https://player.vimeo.com/video/{video_id}')
                except (IndexError, ValueError): pass

            # Strategy 3: Find all likely iframes
            iframes = soup.find_all('iframe')
            for frame in iframes:
                src = frame.get('src', '')
                if src and ('player' in src.lower() or 'embed' in src.lower()):
                    found_urls.add(src)

            # Strategy 4: Find all likely HTML5 video tags
            video_tags = soup.find_all('video')
            for video_tag in video_tags:
                if video_tag.get('src'):
                    found_urls.add(video_tag['src'])
                for source_tag in video_tag.find_all('source'):
                    if source_tag.get('src'):
                        found_urls.add(source_tag['src'])
            
            # Strategy 5: Intelligently parse script tags for player configuration JSON
            import json
            import re
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # Find potential JSON objects within the script tag
                    json_matches = re.findall(r'(\{.*?\})', script.string)
                    for potential_json in json_matches:
                        try:
                            # Clean up the string to be valid JSON
                            clean_json = potential_json.replace("'", '"')
                            data = json.loads(clean_json)
                            
                            # Recursively search the JSON for video URLs
                            def find_video_urls(obj):
                                if isinstance(obj, dict):
                                    for key, value in obj.items():
                                        if isinstance(value, str) and ('.m3u8' in value or '.mp4' in value):
                                            # Check for common keys to prioritize the main video
                                            if key in ['hls', 'video_url', 'file', 'src']:
                                                found_urls.add(value)
                                        elif isinstance(value, (dict, list)):
                                            find_video_urls(value)
                                elif isinstance(obj, list):
                                    for item in obj:
                                        find_video_urls(item)
                            
                            find_video_urls(data)
                        except (json.JSONDecodeError, TypeError):
                            continue

            url_options = list(found_urls)
            # --- Recursive Scrape for Embed URLs ---
            # If the only good URLs we found are embed pages, scrape them too.
            potential_embed_pages = [u for u in found_urls if '/embed/' in u]
            if potential_embed_pages and not any('.m3u8' in u or '.mp4' in u for u in found_urls):
                for embed_page_url in potential_embed_pages:
                    try:
                        embed_response = requests.get(embed_page_url, headers=headers, timeout=10)
                        embed_soup = BeautifulSoup(embed_response.content, 'html.parser')
                        embed_scripts = embed_soup.find_all('script')
                        for script in embed_scripts:
                            if script.string:
                                # Use the same advanced JSON parsing logic on the embed page
                                json_matches = re.findall(r'(\{.*?\})', script.string)
                                for potential_json in json_matches:
                                    try:
                                        clean_json = potential_json.replace("'", '"')
                                        data = json.loads(clean_json)
                                        def find_video_urls_recursive(obj):
                                            if isinstance(obj, dict):
                                                for key, value in obj.items():
                                                    if isinstance(value, str) and ('.m3u8' in value or '.mp4' in value):
                                                        if key in ['hls', 'video_url', 'file', 'src']:
                                                            found_urls.add(value)
                                                    elif isinstance(value, (dict, list)):
                                                        find_video_urls_recursive(value)
                                            elif isinstance(obj, list):
                                                for item in obj:
                                                    find_video_urls_recursive(item)
                                        find_video_urls_recursive(data)
                                    except (json.JSONDecodeError, TypeError):
                                        continue
                    except requests.RequestException:
                        continue # Ignore if the embed page fails to load

            url_options = list(found_urls)
            # Make a best guess for the default embed_url, prioritizing .m3u8
            best_guess = ''
            if url_options:
                m3u8_urls = [u for u in url_options if '.m3u8' in u]
                if m3u8_urls:
                    best_guess = m3u8_urls[0]
                else:
                    # Avoid selecting an embed page as the best guess if we found media files
                    media_urls = [u for u in url_options if '.mp4' in u or '.webm' in u]
                    if media_urls:
                        best_guess = media_urls[0]
                    else:
                        best_guess = url_options[0]

            scraped_title = title['content'] if title else ''
            generated_tags = generate_tags_from_title(scraped_title)

            data = {
                'title': scraped_title,
                'description': description['content'] if description else '',
                'thumbnail_url': thumbnail_url['content'] if thumbnail_url else '',
                'embed_url': best_guess,
                'embed_url_options': url_options,
                'tags': generated_tags,
            }

            return Response(data, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response({"error": f"Failed to fetch URL: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ManualBookmarkCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ManualBookmarkSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            bookmark = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VideoLikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id)
            like, created = VideoLike.objects.get_or_create(user=request.user, video=video)
            if not created:
                like.delete()
                video.likes_count -= 1
                is_liked = False
            else:
                video.likes_count += 1
                is_liked = True
            video.save()
            return Response({'is_liked': is_liked, 'likes_count': video.likes_count}, status=status.HTTP_200_OK)
        except Video.DoesNotExist:
            return Response({'detail': 'Video not found.'}, status=status.HTTP_404_NOT_FOUND)

class VideoLikeStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=404)

        is_liked = VideoLike.objects.filter(video=video, user=request.user).exists()
        return Response({"is_liked": is_liked})

class UsersWhoBookmarkedView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to access this view

    def get(self, request, video_id):
        try:
            bookmarks = Bookmark.objects.filter(video_id=video_id).select_related('user')
            users = [bookmark.user for bookmark in bookmarks if bookmark.user]
            serializer = UserPublicSerializer(users, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
