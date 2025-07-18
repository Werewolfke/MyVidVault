from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import ManualBookmarkSerializer
from operations.models import Video, VideoLike
from users.models import Bookmark
from operations.serializers import UserPublicSerializer

# Create your views here.

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
