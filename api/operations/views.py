from django.contrib.auth.models import User
from django.db.models import Q, Case, When, OuterRef, Subquery, Max, Min, Count
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
        Ensures only one bookmark per video is returned.
        Optimized for large datasets and high concurrency.
        """
        # Use .only() to limit fields, and .iterator() for memory efficiency
        base_queryset = Bookmark.objects.select_related(
            'user', 'user__profile', 'channel', 'channel__collection', 'video'
        ).prefetch_related('video__tags').only(
            'id', 'user', 'channel', 'video', 'title', 'description', 'access', 'created_at', 'updated_at'
        )

        # Apply filters before grouping
        queryset = self._apply_filters(base_queryset)
        queryset = self._apply_search(queryset)

        # Group by video and select the earliest bookmark for each video
        grouped_queryset = queryset.values('video').annotate(
            first_bookmark_id=Min('id')
        ).values_list('first_bookmark_id', flat=True)

        # Filter the queryset to include only the grouped bookmarks
        queryset = queryset.filter(id__in=grouped_queryset)

        # Return QuerySet directly for DRF pagination compatibility
        return self._apply_sorting(queryset)
    # Add per-page cache for high-traffic endpoints
    from django.utils.decorators import method_decorator
    from django.views.decorators.cache import cache_page

    @method_decorator(cache_page(60), name='dispatch')  # Cache each page for 60 seconds
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def _apply_filters(self, queryset):
        """Applies filters for orientation, user, liked_by, following, and tags."""
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

        tag_param = self.request.query_params.get('tag')
        if tag_param:
            # Filter on the video's tags
            queryset = queryset.filter(video__tags__name__iexact=tag_param)

        return queryset.distinct()

    def _apply_search(self, queryset):
        """Applies a search filter across multiple fields."""
        search = self.request.query_params.get('q')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(video__title__icontains=search) |
                Q(video__tags__name__icontains=search)
            )
        return queryset.distinct()

    def _apply_sorting(self, queryset):
        """Applies sorting based on the 'sort' query parameter."""
        sort_param = self.request.query_params.get('sort', 'all')

        if sort_param == 'popular':
            queryset = queryset.annotate(
                bookmark_count=Count('id'),
                like_count=Count('video__likes')
            ).order_by('-bookmark_count', '-like_count')
        elif sort_param == 'random':
            queryset = queryset.order_by('?')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset


class BookmarkDetailAPIView(generics.RetrieveAPIView):
    # This queryset is already well-optimized to prevent N+1 query issues.
    queryset = Bookmark.objects.select_related(
        'user', 'user__profile', 'channel', 'channel__collection', 'video'
    ).prefetch_related('tags')
    serializer_class = BookmarkDetailSerializer
    lookup_field = 'id'