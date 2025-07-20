from rest_framework import serializers
from operations.models import Video, Tag
from users.models import User, Channel, Bookmark

class ManualBookmarkSerializer(serializers.Serializer):
    video = serializers.DictField()
    bookmark = serializers.DictField()

    def validate(self, data):
        video_data = data.get('video', {})
        bookmark_data = data.get('bookmark', {})

        # Fields that must have a non-empty value
        required_video_fields = ['source_url', 'title', 'thumbnail_url', 'embed_url', 'orientation', 'player_type']
        for field in required_video_fields:
            if field not in video_data:
                raise serializers.ValidationError({f'video.{field}': 'This field is required.'})

        required_bookmark_fields = ['channel_id', 'access']
        for field in required_bookmark_fields:
            if not bookmark_data.get(field):
                raise serializers.ValidationError({f'bookmark.{field}': 'This field may not be blank.'})

        # Fields that can be empty (like an empty list or string) but must exist
        if 'tags' not in video_data:
            raise serializers.ValidationError({f'video.tags': 'This field is required.'})
        if 'tags' not in bookmark_data:
            raise serializers.ValidationError({f'bookmark.tags': 'This field is required.'})
        if 'description' not in bookmark_data:
            raise serializers.ValidationError({f'bookmark.description': 'This field is required.'})
            
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        video_data = validated_data['video']
        bookmark_data = validated_data['bookmark']

        # Use update_or_create to safely handle both new and existing videos
        video, created = Video.objects.update_or_create(
            source_url=video_data.get('source_url'),
            defaults={
                'title': video_data.get('title'),
                'thumbnail_url': video_data.get('thumbnail_url'),
                'embed_url': video_data.get('embed_url'),
                'orientation': video_data.get('orientation'),
                'player_type': video_data.get('player_type', 'direct'),
                'created_by': user,
            }
        )

        # If the video was just created, set the creator.
        # If it existed, we don't want to change the original creator.
        if not created:
            video.created_by = video.created_by or user
            video.save()

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
