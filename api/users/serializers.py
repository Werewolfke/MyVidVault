from rest_framework import serializers
from users.models import Profile, Collection, Channel, Bookmark, Follow
from operations.models import Tag
from django.contrib.auth.models import User
from operations.models import Video  # adjust import as needed
from django.conf import settings
from django.core.files.storage import default_storage

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

    class Meta:
        model = Bookmark
        fields = [
            'id', 'title', 'description', 'created_at', 'video',
            'channel', 'collection', 'tags', 'tags_list'
        ]

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        validated_data.pop('collection', None)
        bookmark = super().create(validated_data)
        tag_objs = []
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tag_objs.append(tag)
        bookmark.tags.set(tag_objs)
        return bookmark

class ChannelSerializer(serializers.ModelSerializer):
    bookmarks = BookmarkSerializer(many=True, read_only=True)

    class Meta:
        model = Channel
        fields = ['id', 'name', 'description', 'imageUrl', 'bookmarks']

class CollectionSerializer(serializers.ModelSerializer):
    channels = ChannelSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'name', 'description', 'imageUrl', 'channels']

class UserProfileDetailSerializer(serializers.ModelSerializer):
    collections = serializers.SerializerMethodField()
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    bookmarks_count = serializers.IntegerField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    avatar_url = serializers.SerializerMethodField()

    # Add writable fields for PATCH
    bio = serializers.CharField(allow_blank=True, required=False)
    avatar = serializers.ImageField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Profile
        fields = [
            'username', 'bio', 'avatar', 'avatar_url',
            'collections', 'followers_count', 'following_count',
            'bookmarks_count', 'likes_count'
        ]
        read_only_fields = ['username', 'avatar_url', 'collections', 'followers_count', 'following_count', 'bookmarks_count', 'likes_count']


    def get_collections(self, obj):
        # Use prefetched collections if available (set in view)
        collections = getattr(obj, '_prefetched_collections', None)
        if collections is None:
            from users.models import Collection
            collections = Collection.objects.filter(user=obj.user).prefetch_related('channels')
        return CollectionSerializer(collections, many=True).data


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
        # Handle avatar update
        avatar = validated_data.pop('avatar', None)
        if avatar is not None:
            instance.avatar = avatar
        # Handle bio update
        bio = validated_data.get('bio', None)
        if bio is not None:
            instance.bio = bio
        instance.save()
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