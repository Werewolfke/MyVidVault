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
    list_display = ('id', 'title', 'user', 'orientation', 'created_at')
    search_fields = ('title', 'description', 'tags__name')
    list_filter = ('orientation', 'created_at')

admin.site.register(Tag)
admin.site.register(Video, VideoAdmin)
admin.site.register(VideoLike)
admin.site.register(ContactSubmission)
admin.site.register(Report)
admin.site.register(VideoComment)
admin.site.register(CommentReply)