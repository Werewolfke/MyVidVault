from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from operations.views import BookmarkListAPIView, BookmarkDetailAPIView
from users.views import (
    UserProfileView,
    MyCollectionsListView,
    CollectionChannelsListView,
    BookmarkCreateAPIView,
    MyProfileView,ToggleFollowView,
)
from videos.views import ManualBookmarkCreateView, VideoLikeToggleView,UsersWhoBookmarkedView, VideoLikeStatusView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/profile/me/', MyProfileView.as_view(), name='my-profile'),

    path('api/auth/', include('authsystem.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/videos/', BookmarkListAPIView.as_view(), name='video-list'),
    path('api/bookmarks/', BookmarkListAPIView.as_view(), name='bookmark-list'),
    path('api/bookmarks/<int:id>/', BookmarkDetailAPIView.as_view(), name='bookmark-detail'),
    path('api/bookmarks/create/', BookmarkCreateAPIView.as_view(), name='bookmark-create'),
    path('api/bookmarks/manual-create/', ManualBookmarkCreateView.as_view(), name='manual-bookmark-create'),

    path('api/collections/', MyCollectionsListView.as_view(), name='my-collections'),
    path('api/collections/<int:collection_id>/channels/', CollectionChannelsListView.as_view(), name='collection-channels'),

    path('api/profile/<str:username>/', UserProfileView.as_view(), name='user-profile'),

    # New URL for liking/unliking videos
    path('api/videos/<int:video_id>/like/', VideoLikeToggleView.as_view(), name='video-like-toggle'),
    path('api/videos/<int:video_id>/like-status/', VideoLikeStatusView.as_view(), name='video-like-status'),
    path('api/videos/<int:video_id>/users-bookmarked/', UsersWhoBookmarkedView.as_view(), name='users-who-bookmarked'),
    path('api/users/<int:user_id>/toggle-follow/', ToggleFollowView.as_view(), name='toggle-follow'),

]

