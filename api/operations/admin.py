from django.contrib import admin
from .models import (
    Tag,
    Video,
    VideoLike,
    ContactSubmission,
    Report,
    VideoComment,
    CommentReply,
)

class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'get_user', 'orientation', 'created_at')  # Use 'get_user' method
    search_fields = ('title', 'description', 'tags__name')
    list_filter = ('orientation', 'created_at')

    def get_user(self, obj):
        # Assuming 'user' is a ForeignKey in the Video model
        return obj.user.username if obj.user else None
    get_user.short_description = 'User'  # Display name in admin

admin.site.register(Tag)
admin.site.register(Video, VideoAdmin)
admin.site.register(VideoLike)
admin.site.register(ContactSubmission)
admin.site.register(Report)
admin.site.register(VideoComment)
admin.site.register(CommentReply)