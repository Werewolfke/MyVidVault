from rest_framework import serializers
from operations.models import AuditLog, Report, Video
from users.models import Bookmark
from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.models import Bookmark
from operations.models import Video  # adjust import if needed
from django.core.files.storage import default_storage
from django.conf import settings

User = get_user_model()

class ReportSerializer(serializers.ModelSerializer):
    assigned_to = serializers.StringRelatedField()
    class Meta:
        model = Report
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    moderator = serializers.StringRelatedField()
    class Meta:
        model = AuditLog
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = '__all__'


class UserPublicSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'avatar_url', 'bio']

    def get_avatar_url(self, obj):
        profile = getattr(obj, 'profile', None)
        if profile and getattr(profile, 'avatar', None):
            # Skip file existence check for performance - let the frontend handle 404s
            return profile.avatar.url
        # Return your default image URL
        return settings.MEDIA_URL + 'default.jpg'

    def get_bio(self, obj):
        profile = getattr(obj, 'profile', None)
        return getattr(profile, 'bio', '')

class HomePageBookmarkSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='video.title', read_only=True)
    thumbnail_url = serializers.CharField(source='video.thumbnail_url', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_avatar_url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    channel_name = serializers.CharField(source='channel.name', read_only=True)
    collection_name = serializers.CharField(source='video.collection.name', read_only=True)
    description = serializers.CharField(read_only=True)
    orientation = serializers.CharField(source='video.orientation', read_only=True)
    likes_count = serializers.IntegerField(source='video.likes_count', read_only=True)
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = Bookmark
        fields = [
            'id',
            'title',
            'thumbnail_url',
            'user_username',
            'user_avatar_url',
            'created_at',
            'channel_name',
            'collection_name',
            'description',
            'orientation',
            'likes_count',
            'tags',
        ]

    def get_user_avatar_url(self, obj):
        profile = getattr(obj.user, 'profile', None)
        if profile and getattr(profile, 'avatar', None):
            # Skip file existence check for performance - let the frontend handle 404s
            return profile.avatar.url
        return settings.MEDIA_URL + 'default.jpg'

class VideoDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'embed_url', 'thumbnail_url', 'source_url',
            'orientation', 'likes_count'
        ]

class BookmarkDetailSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    video = VideoDetailSerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = [
            'user', 'id', 'title', 'description', 'created_at',
            'tags', 'video'
        ]

