from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import generics
from users.models import Profile, Bookmark
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, parse_qs
import json

from users.serializers import UserProfileDetailSerializer, BookmarkSerializer, UserProfileSerializer
from .models import Collection, Channel, Follow, User
from .serializers import CollectionSerializer, ChannelSerializer
from operations.models import Video

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileDetailSerializer
    lookup_field = 'user__username'
    
    @method_decorator(cache_page(180))  # Cache for 3 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self):
        from django.db.models import Prefetch, Count
        from users.models import Collection, Channel
        from django.contrib.auth.models import User
        username = self.kwargs.get('username')
        
        # First, get the user and basic profile info
        try:
            user = User.objects.only('id', 'username').get(username=username)
        except User.DoesNotExist:
            raise Http404("User not found")
            
        # Get or create profile without complex aggregations first
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={'bio': '', 'avatar': None}
        )
        
        if created:
            # Create default collection and channel for new profile
            if not user.collections.exists():
                collection = Collection.objects.create(
                    user=user,
                    name=user.username,
                    description=f"{user.username}'s collection"
                )
                Channel.objects.create(
                    collection=collection,
                    name=f"{user.username}'s channel",
                    description=f"Default channel for {user.username}"
                )
        
        # Calculate counts separately to avoid temp file issues
        followers_count = Follow.objects.filter(followed=user).count()
        following_count = Follow.objects.filter(follower=user).count()
        bookmarks_count = Bookmark.objects.filter(user=user).count()
        likes_count = user.video_likes.count()
        
        # Manually set the counts on the profile
        profile._followers_count = followers_count
        profile._following_count = following_count
        profile._bookmarks_count = bookmarks_count
        profile._likes_count = likes_count
        
        # Prefetch collections with limited data
        collections = Collection.objects.filter(user=user).only(
            'id', 'name', 'description', 'imageUrl', 'user_id', 'created_at'
        ).prefetch_related(
            Prefetch(
                'channels',
                queryset=Channel.objects.only('id', 'name', 'description', 'imageUrl', 'collection_id')
            )
        )[:50]  # Limit to prevent large queries
        
        profile._prefetched_collections = list(collections)
        
        return profile

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class MyCollectionsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Prefetch channels for efficiency
        collections = Collection.objects.filter(user=request.user).prefetch_related('channels')
        serializer = CollectionSerializer(collections, many=True)
        return Response(serializer.data)

class CollectionChannelsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, collection_id):
        # Only allow access to own collections
        try:
            collection = Collection.objects.prefetch_related('channels').get(id=collection_id, user=request.user)
        except Collection.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        channels = collection.channels.all()
        serializer = ChannelSerializer(channels, many=True)
        return Response(serializer.data)


# Standard create (manual entry)
class BookmarkCreateAPIView(generics.CreateAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Register the collect_bookmark endpoint in the URL conf

 # Removed MyProfileView since /api/profile/me/ is deprecated; use UserProfileView and PATCH via /api/profile/<str:username>/

class ToggleFollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
            if target_user == request.user:
                return Response({"error": "You cannot follow yourself."}, status=400)

            follow, created = Follow.objects.get_or_create(follower=request.user, followed=target_user)
            if not created:
                follow.delete()
                is_followed = False
            else:
                is_followed = True

            return Response({"is_followed": is_followed})
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

class FollowersListView(APIView):
    """Get list of users who follow a specific user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
            followers = Follow.objects.filter(followed=target_user).select_related('follower__profile')
            followers_data = []
            
            for follow in followers:
                user_data = {
                    'id': follow.follower.id,
                    'username': follow.follower.username,
                    'avatar_url': self.get_avatar_url(follow.follower, request),
                    'followed_at': follow.created_at
                }
                followers_data.append(user_data)
            
            return Response({'followers': followers_data})
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
    
    def get_avatar_url(self, user, request):
        try:
            profile = user.profile
            if profile.avatar and hasattr(profile.avatar, 'url'):
                avatar_path = profile.avatar.name
                if default_storage.exists(avatar_path):
                    return request.build_absolute_uri(profile.avatar.url)
                return profile.avatar.url
        except:
            pass
        default_url = settings.MEDIA_URL + 'default.jpg'
        return request.build_absolute_uri(default_url)

class FollowingListView(APIView):
    """Get list of users that a specific user follows"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
            following = Follow.objects.filter(follower=target_user).select_related('followed__profile')
            following_data = []
            
            for follow in following:
                user_data = {
                    'id': follow.followed.id,
                    'username': follow.followed.username,
                    'avatar_url': self.get_avatar_url(follow.followed, request),
                    'followed_at': follow.created_at
                }
                following_data.append(user_data)
            
            return Response({'following': following_data})
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
    
    def get_avatar_url(self, user, request):
        try:
            profile = user.profile
            if profile.avatar and hasattr(profile.avatar, 'url'):
                avatar_path = profile.avatar.name
                if default_storage.exists(avatar_path):
                    return request.build_absolute_uri(profile.avatar.url)
                return profile.avatar.url
        except:
            pass
        default_url = settings.MEDIA_URL + 'default.jpg'
        return request.build_absolute_uri(default_url)

class CheckFollowStatusView(APIView):
    """Check if current user follows a specific user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
            if target_user == request.user:
                return Response({"is_followed": False, "is_self": True})
            
            is_followed = Follow.objects.filter(follower=request.user, followed=target_user).exists()
            return Response({"is_followed": is_followed, "is_self": False})
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

class VideoMetadataExtractorView(APIView):
    """Extract video metadata from URL"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        url = request.data.get('url')
        if not url:
            return Response(
                {'error': 'URL is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Extract metadata from URL
            metadata = self.extract_metadata(url)
            return Response(metadata, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Failed to extract metadata: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def extract_metadata(self, url):
        """Extract video metadata from various video platforms"""
        
        # Clean and validate URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse URL to identify platform
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Platform-specific extraction
        if 'youtube.com' in domain or 'youtu.be' in domain:
            return self.extract_youtube_metadata(url, parsed_url)
        elif 'vimeo.com' in domain:
            return self.extract_vimeo_metadata(url, parsed_url)
        elif 'pornhub.com' in domain:
            return self.extract_pornhub_metadata(url, parsed_url)
        elif 'xvideos.com' in domain:
            return self.extract_xvideos_metadata(url, parsed_url)
        elif 'redtube.com' in domain:
            return self.extract_redtube_metadata(url, parsed_url)
        elif 'xhamster.com' in domain:
            return self.extract_xhamster_metadata(url, parsed_url)
        else:
            # Generic extraction for other sites
            return self.extract_generic_metadata(url)
    
    def extract_youtube_metadata(self, url, parsed_url):
        """Extract YouTube video metadata"""
        # Extract video ID
        video_id = None
        if 'youtu.be' in parsed_url.netloc:
            video_id = parsed_url.path.lstrip('/')
        elif 'youtube.com' in parsed_url.netloc:
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get('v', [None])[0]
        
        if not video_id:
            raise Exception("Could not extract YouTube video ID")
        
        # Try to get metadata from YouTube's oEmbed API
        try:
            oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
            response = requests.get(oembed_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'video': {
                    'title': data.get('title', ''),
                    'source_url': url,
                    'thumbnail_url': data.get('thumbnail_url', ''),
                    'embed_url': f"https://www.youtube.com/embed/{video_id}",
                    'orientation': 'sfw'  # Default for YouTube
                },
                'suggested_tags': self.extract_tags_from_title(data.get('title', '')),
                'channel_name': data.get('author_name', ''),
                'platform': 'YouTube'
            }
        except:
            # Fallback to generic extraction
            return self.extract_generic_metadata(url)
    
    def extract_vimeo_metadata(self, url, parsed_url):
        """Extract Vimeo video metadata"""
        # Extract video ID from URL
        path_parts = parsed_url.path.strip('/').split('/')
        video_id = path_parts[0] if path_parts else None
        
        if not video_id or not video_id.isdigit():
            raise Exception("Could not extract Vimeo video ID")
        
        try:
            # Use Vimeo's oEmbed API
            oembed_url = f"https://vimeo.com/api/oembed.json?url={url}"
            response = requests.get(oembed_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'video': {
                    'title': data.get('title', ''),
                    'source_url': url,
                    'thumbnail_url': data.get('thumbnail_url', ''),
                    'embed_url': f"https://player.vimeo.com/video/{video_id}",
                    'orientation': 'sfw'  # Default for Vimeo
                },
                'suggested_tags': self.extract_tags_from_title(data.get('title', '')),
                'channel_name': data.get('author_name', ''),
                'platform': 'Vimeo'
            }
        except:
            return self.extract_generic_metadata(url)
    
    def extract_pornhub_metadata(self, url, parsed_url):
        """Extract Pornhub video metadata"""
        return self.extract_generic_metadata(url, default_orientation='straight')
    
    def extract_xvideos_metadata(self, url, parsed_url):
        """Extract XVideos video metadata"""
        return self.extract_generic_metadata(url, default_orientation='straight')
    
    def extract_redtube_metadata(self, url, parsed_url):
        """Extract RedTube video metadata"""
        return self.extract_generic_metadata(url, default_orientation='straight')
    
    def extract_xhamster_metadata(self, url, parsed_url):
        """Extract XHamster video metadata"""
        return self.extract_generic_metadata(url, default_orientation='straight')
    
    def extract_generic_metadata(self, url, default_orientation='sfw'):
        """Generic metadata extraction using web scraping"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = None
            # Try multiple methods to get title
            title_selectors = [
                'meta[property="og:title"]',
                'meta[name="twitter:title"]',
                'title',
                'h1'
            ]
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    if element.name == 'meta':
                        title = element.get('content', '').strip()
                    else:
                        title = element.get_text().strip()
                    if title:
                        break
            
            # Extract thumbnail
            thumbnail_url = None
            thumbnail_selectors = [
                'meta[property="og:image"]',
                'meta[name="twitter:image"]',
                'meta[property="og:image:url"]',
                'link[rel="image_src"]'
            ]
            
            for selector in thumbnail_selectors:
                element = soup.select_one(selector)
                if element:
                    thumbnail_url = element.get('content') or element.get('href')
                    if thumbnail_url:
                        break
            
            # Extract description for tag suggestions
            description = None
            desc_selectors = [
                'meta[property="og:description"]',
                'meta[name="twitter:description"]',
                'meta[name="description"]'
            ]
            
            for selector in desc_selectors:
                element = soup.select_one(selector)
                if element:
                    description = element.get('content', '').strip()
                    if description:
                        break
            
            # Generate suggested tags
            suggested_tags = self.extract_tags_from_title(title or '')
            if description:
                suggested_tags.extend(self.extract_tags_from_title(description))
            
            # Remove duplicates while preserving order
            suggested_tags = list(dict.fromkeys(suggested_tags))
            
            return {
                'video': {
                    'title': title or 'Untitled Video',
                    'source_url': url,
                    'thumbnail_url': thumbnail_url or '',
                    'embed_url': '',  # Will need to be set manually
                    'orientation': default_orientation
                },
                'suggested_tags': suggested_tags[:10],  # Limit to 10 tags
                'channel_name': '',
                'platform': 'Generic'
            }
        
        except Exception as e:
            raise Exception(f"Failed to extract metadata: {str(e)}")
    
    def extract_tags_from_title(self, text):
        """Extract potential tags from title or description"""
        if not text:
            return []
        
        # Convert to lowercase and split into words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common words and short words
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his',
            'her', 'its', 'our', 'their', 'video', 'videos', 'clip', 'clips', 'watch', 'watching', 'hd', 'free'
        }
        
        # Filter words
        filtered_words = [
            word for word in words 
            if len(word) >= 3 and word not in common_words and word.isalpha()
        ]
        
        # Take first 10 unique words
        return list(dict.fromkeys(filtered_words))[:10]

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def collect_bookmark(request):
    """
    Duplicate an existing bookmark for the current user into a target collection/channel.
    Expects: { bookmark: <id>, collection: <id>, channel: <id> }
    """
    bookmark_id = request.data.get('bookmark')
    collection_id = request.data.get('collection')
    channel_id = request.data.get('channel')
    if not bookmark_id or not collection_id or not channel_id:
        return Response({'error': 'bookmark, collection, and channel are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        orig = Bookmark.objects.select_related('video').get(id=bookmark_id)
    except Bookmark.DoesNotExist:
        return Response({'error': 'Source bookmark not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Copy all fields except user, collection, channel
    new_bm = Bookmark.objects.create(
        user=request.user,
        video=orig.video,
        channel_id=channel_id,
        title=orig.title,
        description=orig.description,
        access=orig.access,
    )
    # Copy tags
    new_bm.tags.set(orig.tags.all())
    new_bm.save()
    from users.serializers import BookmarkSerializer
    return Response(BookmarkSerializer(new_bm, context={'request': request}).data, status=status.HTTP_201_CREATED)