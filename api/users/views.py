from django.shortcuts import get_object_or_404
from rest_framework import generics
from users.models import Profile, Bookmark
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from users.serializers import UserProfileDetailSerializer, BookmarkSerializer, UserProfileSerializer
from .models import Collection, Channel
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
        collections = Collection.objects.filter(user=request.user)
        serializer = CollectionSerializer(collections, many=True)
        return Response(serializer.data)

class CollectionChannelsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, collection_id):
        # Only allow access to own collections
        try:
            collection = Collection.objects.get(id=collection_id, user=request.user)
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