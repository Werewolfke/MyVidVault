# Models for moderator actions, assignments, and audit logs
from django.db import models
from django.conf import settings
from operations.models import Video, Report
from users.models import Bookmark

class ModeratorAssignment(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='assignment')
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

class ModeratorAuditLog(models.Model):
    ACTION_CHOICES = [
        ('edit_video', 'Edit Video'),
        ('edit_bookmark', 'Edit Bookmark'),
        ('assign_report', 'Assign Report'),
        ('approve_report', 'Approve Report'),
        ('deny_report', 'Deny Report'),
    ]
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=32, choices=ACTION_CHOICES)
    video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL)
    bookmark = models.ForeignKey(Bookmark, null=True, blank=True, on_delete=models.SET_NULL)
    report = models.ForeignKey(Report, null=True, blank=True, on_delete=models.SET_NULL)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
