from django.contrib import admin
from django.utils import timezone
from operations.models import (
    Tag,
    Video,
    VideoLike,
    ContactSubmission,
    Report,
    VideoComment,
    CommentReply,
)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'bookmark', 'user', 'report_type', 'is_resolved', 'created_at')
    actions = ['approve_report', 'deny_report']

    def approve_report(self, request, queryset):
        for report in queryset:
            report.is_resolved = True
            report.resolved_at = timezone.now()
            report.save(update_fields=['is_resolved', 'resolved_at'])
            # Video stays private
    approve_report.short_description = 'Approve selected reports (video stays private)'

    def deny_report(self, request, queryset):
        for report in queryset:
            if report.bookmark:
                video = report.bookmark.video
            else:
                video = None
            if video:
                video.access = 'public'
                video.save(update_fields=['access'])
            report.is_resolved = True
            report.resolved_at = timezone.now()
            report.save(update_fields=['is_resolved', 'resolved_at'])
    deny_report.short_description = 'Deny selected reports (video set to public)'
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
    list_display = ('id', 'title', 'get_user', 'orientation', 'created_at')
    search_fields = ('title', 'description', 'tags__name')
    list_filter = ('orientation', 'created_at')

    def get_user(self, obj):
        return obj.user.username if hasattr(obj, 'user') and obj.user else None
    get_user.short_description = 'User'

admin.site.register(Tag)
admin.site.register(Video, VideoAdmin)
admin.site.register(VideoLike)
admin.site.register(ContactSubmission)
admin.site.register(VideoComment)
admin.site.register(CommentReply)