from rest_framework import serializers
from operations.models import Video, Tag
from users.models import User, Channel, Bookmark

class ManualBookmarkSerializer(serializers.Serializer):
    video = serializers.DictField()
    bookmark = serializers.DictField()

    def validate(self, data):
        # Validate video fields
        video_data = data.get('video', {})
        bookmark_data = data.get('bookmark', {})

        # Add your validation logic here (required fields, etc.)
        required_video_fields = ['source_url', 'title', 'thumbnail_url', 'embed_url', 'orientation', 'tags']
        for field in required_video_fields:
            if not video_data.get(field):
                raise serializers.ValidationError({f'video': {field: ['This field is required.']}})
        required_bookmark_fields = ['channel_id', 'description', 'access', 'tags']
        for field in required_bookmark_fields:
            if not bookmark_data.get(field):
                raise serializers.ValidationError({f'bookmark': {field: ['This field is required.']}})
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        video_data = validated_data['video']
        bookmark_data = validated_data['bookmark']

        # Create or get the video
        video, _ = Video.objects.get_or_create(
            source_url=video_data['source_url'],
            defaults={
                'title': video_data['title'],
                'thumbnail_url': video_data['thumbnail_url'],
                'embed_url': video_data['embed_url'],
                'orientation': video_data['orientation'],
                'created_by': user,
            }
        )
        # Convert tag names to Tag objects for video
        video_tags = []
        for tag_name in video_data['tags']:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            video_tags.append(tag)
        video.tags.set(video_tags)
        video.save()

        channel = Channel.objects.get(id=bookmark_data['channel_id'])

        # Check for existing bookmark
        existing = Bookmark.objects.filter(user=user, channel=channel, video=video).first()
        if existing:
            raise serializers.ValidationError("You have already bookmarked this video in this channel.")

        bookmark = Bookmark.objects.create(
            user=user,
            video=video,
            channel=channel,
            description=bookmark_data['description'],
            access=bookmark_data['access'],
        )
        # Convert tag names to Tag objects for bookmark
        bookmark_tags = []
        for tag_name in bookmark_data['tags']:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            bookmark_tags.append(tag)
        bookmark.tags.set(bookmark_tags)
        bookmark.save()
        return bookmark

    def to_representation(self, instance):
        # Return the bookmark detail as response
        from users.serializers import BookmarkSerializer
        return BookmarkSerializer(instance).data