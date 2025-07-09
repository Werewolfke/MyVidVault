from django.shortcuts import get_object_or_404
from rest_framework import generics
from users.models import Profile, Bookmark
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from users.serializers import UserProfileDetailSerializer, BookmarkSerializer, UserProfileSerializer
from .models import Collection, Channel, Follow, User
from .serializers import CollectionSerializer, ChannelSerializer
from operations.models import Video

class UserProfileView(generics.RetrieveAPIView):
    queryset = Profile.objects.select_related('user')
    serializer_class = UserProfileDetailSerializer  # Use the detailed serializer
    lookup_field = 'user__username'

    def get_object(self):
        username = self.kwargs.get('username')
        profile = get_object_or_404(Profile, user__username=username)
        # Optionally, add privacy logic here
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

class BookmarkCreateAPIView(generics.CreateAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user.profile, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user.profile, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

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