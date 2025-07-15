from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

from operations.views import BookmarkListAPIView, BookmarkDetailAPIView, report_video
from users.views import (
    UserProfileView,
    MyCollectionsListView,
    CollectionChannelsListView,
    BookmarkCreateAPIView,
    ToggleFollowView,
    VideoMetadataExtractorView,
    FollowersListView,
    FollowingListView,
    CheckFollowStatusView,
    collect_bookmark,
)
from videos.views import ManualBookmarkCreateView, VideoLikeToggleView,UsersWhoBookmarkedView, VideoLikeStatusView
from authsystem.views import RegisterView, LoginView, get_csrf_token, LogoutView, PasswordResetRequestView, PasswordResetConfirmView
import debug_toolbar
from django.conf import settings
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
 # Removed 'api/profile/me/' endpoint; use 'api/profile/<str:username>/' for user profiles

    # Authentication endpoints
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/csrf/', get_csrf_token, name='get-csrf-token'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('api/auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    path('api/videos/', BookmarkListAPIView.as_view(), name='video-list'),
    path('api/bookmarks/', BookmarkListAPIView.as_view(), name='bookmark-list'),
    path('api/bookmarks/<int:id>/', BookmarkDetailAPIView.as_view(), name='bookmark-detail'),
    path('api/bookmarks/create/', BookmarkCreateAPIView.as_view(), name='bookmark-create'),
    path('api/bookmarks/collect/', collect_bookmark, name='bookmark-collect'),
    path('api/bookmarks/extract-metadata/', VideoMetadataExtractorView.as_view(), name='bookmark-extract-metadata'),
    path('api/bookmarks/manual-create/', ManualBookmarkCreateView.as_view(), name='manual-bookmark-create'),

    path('api/collections/', MyCollectionsListView.as_view(), name='my-collections'),
    path('api/collections/<int:collection_id>/channels/', CollectionChannelsListView.as_view(), name='collection-channels'),

    path('api/profile/<str:username>/', UserProfileView.as_view(), name='user-profile'),

    # New URL for liking/unliking videos
    path('api/videos/<int:video_id>/like/', VideoLikeToggleView.as_view(), name='video-like-toggle'),
    path('api/videos/<int:video_id>/like-status/', VideoLikeStatusView.as_view(), name='video-like-status'),
    path('api/videos/<int:video_id>/users-bookmarked/', UsersWhoBookmarkedView.as_view(), name='users-who-bookmarked'),
    
    # Follow/Unfollow functionality
    path('api/users/<int:user_id>/toggle-follow/', ToggleFollowView.as_view(), name='toggle-follow'),
    path('api/users/<int:user_id>/follow-status/', CheckFollowStatusView.as_view(), name='check-follow-status'),
    path('api/users/<int:user_id>/followers/', FollowersListView.as_view(), name='followers-list'),
    path('api/users/<int:user_id>/following/', FollowingListView.as_view(), name='following-list'),

    # Reporting endpoint
    path('api/report/', report_video, name='report-video'),

    # Moderator endpoints
    path('api/moderation/', include('moderation.urls')),
]
    
# Enable django-debug-toolbar in DEBUG mode
if getattr(settings, 'DEBUG', False):
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

