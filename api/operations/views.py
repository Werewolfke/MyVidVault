from django.contrib.auth.models import User
from django.db.models import Q, Case, When, OuterRef, Subquery, Max
from rest_framework import generics
from users.models import Bookmark, Follow
from .serializers import HomePageBookmarkSerializer, BookmarkDetailSerializer
from operations.models import VideoLike
from rest_framework.permissions import IsAuthenticatedOrReadOnly
import random


class BookmarkListAPIView(generics.ListAPIView):
    """
    API view to list bookmarks with advanced filtering, searching, and sorting.
    """
    serializer_class = HomePageBookmarkSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Builds the queryset for bookmarks based on query parameters.
        """
        # Start with a base queryset with optimized related object fetching
        queryset = Bookmark.objects.select_related(
            'user',
            'user__profile',
            'channel',
            'channel__collection',
            'video'
        ).prefetch_related('tags')

        queryset = self._apply_filters(queryset)
        queryset = self._apply_search(queryset)
        queryset = self._apply_sorting(queryset)

        return queryset

    def _apply_filters(self, queryset):
        """Applies filters for orientation, user, and liked_by."""
        orientation = self.request.query_params.get('orientation')
        if orientation and orientation != 'all':
            queryset = queryset.filter(video__orientation=orientation)

        user_param = self.request.query_params.get('user')
        if user_param:
            queryset = queryset.filter(user__username=user_param)

        liked_by_param = self.request.query_params.get('liked_by')
        if liked_by_param:
            liked_video_ids = VideoLike.objects.filter(
                user__username=liked_by_param
            ).values_list('video_id', flat=True)
            queryset = queryset.filter(video_id__in=liked_video_ids)

        following = self.request.query_params.get('following')
        if following == 'true' and self.request.user.is_authenticated:
            followed_users = Follow.objects.filter(follower=self.request.user).values_list('followed_id', flat=True)
            queryset = queryset.filter(user_id__in=followed_users)

        return queryset

    def _apply_search(self, queryset):
        """Applies a search filter across multiple fields."""
        search = self.request.query_params.get('q')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(video__title__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()
        return queryset

    def _apply_sorting(self, queryset):
        """Applies sorting based on the 'sort' query parameter."""
        sort_param = self.request.query_params.get('sort', 'all')

        if sort_param == 'random':
            # simplified random ordering
            return queryset.order_by('?')

        # Default sort: 'all', latest bookmarks first.
        return queryset.order_by('-created_at')


class BookmarkDetailAPIView(generics.RetrieveAPIView):
    # This queryset is already well-optimized to prevent N+1 query issues.
    queryset = Bookmark.objects.select_related(
        'user', 'user__profile', 'channel', 'channel__collection', 'video'
    ).prefetch_related('tags')
    serializer_class = BookmarkDetailSerializer
    lookup_field = 'id'