from django.db import models
from django.conf import settings
from users.models import Bookmark

# Choices
PLAYER_CHOICES = [
    ('direct', 'Direct Player'),
    ('iframe', 'Iframe Player'),
]

ORIENTATION_CHOICES = [
    ('straight', 'Straight'),
    ('gay', 'Gay'),
    ('bi', 'Bi'),
    ('trans', 'Trans'),
    ('sfw', 'SFW'),
]

REPORT_TYPE_CHOICES = [
    ('broken_source', 'Broken Source'),
    ('broken_thumbnail', 'Broken Thumbnail'),
    ('broken_embed', 'Broken Embed'),
    ('wrong_orientation', 'Wrong Orientation'),
    ('request_moderation', 'Request Moderation'),
]

# Models
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower().replace(' ', '')
        super().save(*args, **kwargs)

class Video(models.Model):
    source_url = models.URLField(max_length=2083, blank=True, null=True)
    title = models.CharField(max_length=300)
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    embed_url = models.URLField(max_length=500, blank=True, null=True)
    player_type = models.CharField(
        max_length=10,
        choices=PLAYER_CHOICES,
        default='direct',
        help_text="The preferred player type for this video (direct link or iframe)."
    )
    orientation = models.CharField(
        max_length=10,
        choices=ORIENTATION_CHOICES,
        blank=True,
        null=True,
        help_text="Video orientation category"
    )
    tags = models.ManyToManyField('Tag', blank=True, related_name='videos')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_videos',
        help_text="User who originally added this video to the platform."
    )
    likes_count = models.PositiveIntegerField(default=0, help_text="Cached count of likes for this video")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at'], name='vid_created_idx'),
            models.Index(fields=['orientation', 'created_at'], name='vid_orient_crt_idx'),
            models.Index(fields=['likes_count'], name='vid_likes_idx'),
        ]

    def __str__(self):
        return self.title

class VideoLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='video_likes')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} likes {self.video.title}"

class ContactSubmission(models.Model):
    """Stores submissions from the contact form."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Contact from {self.name} ({self.email}) - Subject: {self.subject}"

    class Meta:
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"
        ordering = ['-submitted_at']

class Report(models.Model):
    bookmark = models.ForeignKey(Bookmark, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_made')
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True, help_text="Internal notes for administrators regarding the report.")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['bookmark', 'user']),
            models.Index(fields=['report_type']),
            models.Index(fields=['is_resolved', 'created_at']),
        ]

    def __str__(self):
        return f"Report for '{self.bookmark.title}' by {self.user.username if self.user else 'Anonymous'} - {self.get_report_type_display()}"

class VideoComment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='video_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on video {self.video.id}"

class CommentReply(models.Model):
    comment = models.ForeignKey(VideoComment, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comment_replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = 'Comment replies'

    def __str__(self):
        return f"Reply by {self.user.username} on comment {self.comment.id}"
