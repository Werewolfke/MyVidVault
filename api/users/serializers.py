from rest_framework import serializers
from users.models import Profile, Collection, Channel, Bookmark, Follow
from operations.models import Tag
from django.contrib.auth.models import User
from operations.models import Video  # adjust import as needed
from django.conf import settings
from django.core.files.storage import default_storage

class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for follow lists"""
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar_url']
    
    def get_avatar_url(self, obj):
        request = self.context.get('request')
        try:
            profile = obj.profile
            if profile.avatar and hasattr(profile.avatar, 'url'):
                avatar_path = profile.avatar.name
                if default_storage.exists(avatar_path):
                    if request is not None:
                        return request.build_absolute_uri(profile.avatar.url)
                    return profile.avatar.url
        except:
            pass
        # Return default image URL
        default_url = settings.MEDIA_URL + 'default.jpg'
        if request is not None:
            return request.build_absolute_uri(default_url)
        return default_url

class FollowSerializer(serializers.ModelSerializer):
    """Serializer for follow relationships"""
    follower = UserBasicSerializer(read_only=True)
    followed = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followed', 'created_at']

class BookmarkSerializer(serializers.ModelSerializer):
    channel = serializers.PrimaryKeyRelatedField(
        queryset=Channel.objects.all(), required=False, allow_null=True
    )
    collection = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(), required=False, allow_null=True
    )
    # Write-only for input
    tags = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )
    # Read-only for output
    tags_list = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='name', source='tags'
    )
    # For collect API: allow passing bookmark id
    bookmark = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = Bookmark
        fields = [
            'id', 'title', 'description', 'created_at', 'video',
            'channel', 'collection', 'tags', 'tags_list', 'bookmark'
        ]

    def create(self, validated_data):
        from operations.utils import create_or_get_tags
        
        tags_data = validated_data.pop('tags', [])
        validated_data.pop('collection', None)
        bookmark = super().create(validated_data)
        
        # Use utility function to create/get tags
        tag_objs = create_or_get_tags(tags_data)
        bookmark.tags.set(tag_objs)
        return bookmark

class ChannelSerializer(serializers.ModelSerializer):
    bookmarks = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = ['id', 'name', 'description', 'imageUrl', 'bookmarks']

    def get_bookmarks(self, obj):
        # Skip bookmarks if requested for performance
        if self.context.get('skip_bookmarks', False):
            return []
        return BookmarkSerializer(obj.bookmarks.all(), many=True, context=self.context).data

class CollectionSerializer(serializers.ModelSerializer):
    channels = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ['id', 'name', 'description', 'imageUrl', 'channels']

    def get_channels(self, obj):
        # Use prefetched channels if available
        channels = getattr(obj, 'prefetched_channels', obj.channels.all())
        return ChannelSerializer(channels, many=True, context=self.context).data

class UserProfileDetailSerializer(serializers.ModelSerializer):
    collections = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    bookmarks_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    avatar_url = serializers.SerializerMethodField()

    # Add writable fields for PATCH
    bio = serializers.CharField(allow_blank=True, required=False)
    avatar = serializers.ImageField(required=False, allow_null=True, write_only=True)

    is_moderator = serializers.BooleanField(read_only=True)
    class Meta:
        model = Profile
        fields = [
            'user_id', 'username', 'bio', 'avatar', 'avatar_url',
            'collections', 'followers_count', 'following_count',
            'bookmarks_count', 'likes_count', 'is_moderator'
        ]
        read_only_fields = ['user_id', 'username', 'avatar_url', 'collections', 'followers_count', 'following_count', 'bookmarks_count', 'likes_count', 'is_moderator']

    def get_followers_count(self, obj):
        return getattr(obj, '_followers_count', 0)
    
    def get_following_count(self, obj):
        return getattr(obj, '_following_count', 0)
    
    def get_bookmarks_count(self, obj):
        return getattr(obj, '_bookmarks_count', 0)
    
    def get_likes_count(self, obj):
        return getattr(obj, '_likes_count', 0)


    def get_collections(self, obj):
        # Use prefetched collections if available (set in view)
        collections = getattr(obj, '_prefetched_collections', None)
        if collections is None:
            # Fallback to efficient query if not prefetched
            from users.models import Collection
            collections = Collection.objects.filter(user=obj.user).prefetch_related(
                'channels'
            ).only('id', 'name', 'description', 'imageUrl', 'created_at')
        
        # Use optimized serializer context to avoid N+1 queries
        serializer_context = self.context.copy() if self.context else {}
        serializer_context['skip_bookmarks'] = True  # Skip bookmark serialization for performance
        return CollectionSerializer(collections, many=True, context=serializer_context).data


    # Count fields now use annotated/attached values from the view for efficiency

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        # Check if avatar exists and file is present
        if obj.avatar and hasattr(obj.avatar, 'url'):
            avatar_path = obj.avatar.name
            if default_storage.exists(avatar_path):
                if request is not None:
                    return request.build_absolute_uri(obj.avatar.url)
                return obj.avatar.url
        # Return a default image URL (absolute if possible)
        default_url = settings.MEDIA_URL + 'default.jpg'
        if request is not None:
            return request.build_absolute_uri(default_url)
        return default_url

    def update(self, instance, validated_data):
        import logging
        logger = logging.getLogger("profile_avatar_upload")
        avatar = validated_data.pop('avatar', None)
        logger.info(f"Avatar in validated_data: {avatar}")
        if avatar is not None:
            instance.avatar = avatar
            logger.info(f"Saving avatar for user {instance.user.username} to {instance.avatar.name}")
        else:
            logger.info(f"No avatar provided for user {instance.user.username}")
        bio = validated_data.get('bio', None)
        if bio is not None:
            instance.bio = bio
        instance.save()
        logger.info(f"Profile saved for user {instance.user.username}. Avatar path: {instance.avatar.name if instance.avatar else 'None'}")
        return instance

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    avatar_url = serializers.SerializerMethodField()
    default_bookmark_orientation = serializers.CharField(required=False, allow_blank=True)
    default_bookmark_collection = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(), required=False, allow_null=True
    )
    notify_on_follow = serializers.BooleanField(required=False)
    notify_on_own_video_bookmarked = serializers.BooleanField(required=False)
    notify_on_new_bookmark_from_followed_user = serializers.BooleanField(required=False)
    notify_on_own_video_liked = serializers.BooleanField(required=False)

    class Meta:
        model = Profile
        fields = [
            "username",
            "email",
            "bio",
            "avatar_url",
            "default_bookmark_orientation",
            "default_bookmark_collection",
            "notify_on_follow",
            "notify_on_own_video_bookmarked",
            "notify_on_new_bookmark_from_followed_user",
            "notify_on_own_video_liked",
        ]

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        # Check if avatar exists and file is present
        if obj.avatar and hasattr(obj.avatar, 'url'):
            avatar_path = obj.avatar.name
            if default_storage.exists(avatar_path):
                if request is not None:
                    return request.build_absolute_uri(obj.avatar.url)
                return obj.avatar.url
        # Return a default image URL (absolute if possible)
        default_url = settings.MEDIA_URL + 'default.jpg'
        if request is not None:
            return request.build_absolute_uri(default_url)
        return default_url