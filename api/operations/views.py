from operations.models import Report, Video, VideoLike
from users.models import Bookmark, Follow
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth.models import User
from django.db.models import Q, Case, When, OuterRef, Subquery, Max, Min, Count
from .serializers import HomePageBookmarkSerializer, BookmarkDetailSerializer
import random

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_video(request):
    """
    Report a video or bookmark. Sets video access to private immediately.
    Expects: { video_id: <id>, bookmark_id: <id>, report_type: <str>, notes: <str> }
    """
    video_id = request.data.get('video_id')
    bookmark_id = request.data.get('bookmark_id')
    report_type = request.data.get('report_type')
    notes = request.data.get('notes', '')
    if not video_id and not bookmark_id:
        return Response({'error': 'video_id or bookmark_id required.'}, status=status.HTTP_400_BAD_REQUEST)
    if not report_type:
        return Response({'error': 'report_type required.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        if bookmark_id:
            bookmark = Bookmark.objects.get(id=bookmark_id)
            bookmark.access = 'private'
            bookmark.save(update_fields=['access'])
            Report.objects.create(
                bookmark=bookmark,
                user=request.user,
                report_type=report_type,
                notes=notes,
            )
            return Response({'success': True}, status=status.HTTP_201_CREATED)
        elif video_id:
            # If only video_id is provided, just create the report (no access change)
            Report.objects.create(
                bookmark=None,
                user=request.user,
                report_type=report_type,
                notes=notes,
            )
            return Response({'success': True}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'video_id or bookmark_id required.'}, status=status.HTTP_400_BAD_REQUEST)
    except (Video.DoesNotExist, Bookmark.DoesNotExist):
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    # ...existing code...


class BookmarkListAPIView(generics.ListAPIView):
    """
    API view to list bookmarks with advanced filtering, searching, and sorting.
    """
    serializer_class = HomePageBookmarkSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        from django.core.cache import cache
        cache_key = self._build_cache_key()
        cached_qs = cache.get(cache_key)
        if cached_qs is not None:
            return cached_qs
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

        # Exclude private bookmarks
        queryset = base_queryset.exclude(access='private')
        # Apply filters before grouping
        queryset = self._apply_filters(queryset)
        queryset = self._apply_search(queryset)

        # Group by video and select the earliest bookmark for each video
        grouped_queryset = queryset.values('video').annotate(
            first_bookmark_id=Min('id')
        ).values_list('first_bookmark_id', flat=True)
        queryset = queryset.filter(id__in=grouped_queryset)
        # Return QuerySet directly for DRF pagination compatibility
        return self._apply_sorting(queryset)
        cache.set(cache_key, result, 300)  # Cache for 5 minutes
        return result

    def _build_cache_key(self):
        params = self.request.query_params
        key_parts = [
            'bookmark_list',
            str(params.get('orientation', 'all')),
            str(params.get('user', '')),
            str(params.get('liked_by', '')),
            str(params.get('following', '')),
            str(params.get('tag', '')),
            str(params.get('q', '')),
            str(params.get('sort', 'all')),
            str(self.request.query_params.get('page', '1')),
        ]
        return ':'.join(key_parts)
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


from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class BookmarkDetailAPIView(generics.RetrieveAPIView):
    serializer_class = BookmarkDetailSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        # Highly optimized queryset with minimal fields and optimized joins
        return Bookmark.objects.select_related(
            'user', 
            'user__profile', 
            'video'
        ).prefetch_related(
            'tags'
        ).only(
            # Bookmark fields
            'id', 'title', 'description', 'created_at',
            # User fields
            'user__id', 'user__username',
            # Profile fields  
            'user__profile__avatar', 'user__profile__bio',
            # Video fields
            'video__id', 'video__title', 'video__embed_url', 
            'video__thumbnail_url', 'video__source_url',
            'video__orientation', 'video__likes_count'
        )
    
    @method_decorator(cache_page(300))  # Cache for 5 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)