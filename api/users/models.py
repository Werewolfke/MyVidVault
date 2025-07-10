from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.deconstruct import deconstructible
from django.conf import settings
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os

# Choices
ORIENTATION_CHOICES = [
    ('straight', 'Straight'),
    ('gay', 'Gay'),
    ('bi', 'Bi'),
    ('trans', 'Trans'),
    ('sfw', 'SFW')
]

ACCESS_CHOICES = [
    ('private', 'Private'),
    ('public', 'Public'),
    ('adult', 'Adult'),
]

NOTIFICATION_TYPE_CHOICES = [
    ('follow', 'Follow'),
    ('bookmark_save', 'Bookmark Save'), 
    ('new_content', 'New Content'), 
    ('system', 'System Message'),
    ('video_like', 'Video Like'),
    ('video_bookmark', 'Video Bookmark'),
]

SUBSCRIPTION_TIER_CHOICES = [
    ('premium', 'Premium'),
    # Add other tiers here if needed in the future
]

@deconstructible
class AvatarUploadTo:
    def __call__(self, instance, filename):
        ext = os.path.splitext(filename)[1].lower()
        username = instance.user.username
        return f"avatars/{username}{ext}"

def avatar_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    username = instance.user.username
    return f"avatars/{username}{ext}"

class Profile(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=["user"], name="profile_user_idx"),
        ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to=avatar_upload_to, blank=True, null=True)

    # --- User Preferences ---
    default_bookmark_orientation = models.CharField(
        max_length=15,
        choices=ORIENTATION_CHOICES,
        blank=True,
        null=True,
        help_text="Default orientation to pre-fill when creating a new bookmark."
    )
    default_bookmark_collection = models.ForeignKey(
        'Collection',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Default collection to pre-select when creating a new bookmark."
    )

    # Notification Preferences
    notify_on_follow = models.BooleanField(
        default=True,
        help_text="Receive a notification when someone starts following you."
    )
    notify_on_own_video_bookmarked = models.BooleanField(
        default=True,
        help_text="Receive a notification when someone bookmarks one of your videos."
    )
    notify_on_new_bookmark_from_followed_user = models.BooleanField(
        default=True,
        help_text="Receive a notification when a user you follow creates a new public bookmark."
    )
    notify_on_own_video_liked = models.BooleanField(
        default=True,
        help_text="Receive a notification when someone likes one of your videos."
    )
    # --- End User Preferences ---

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.avatar:
            username = self.user.username
            avatar_path = self.avatar.name

            from django.core.files.storage import default_storage

            if default_storage.exists(avatar_path):
                with default_storage.open(avatar_path, 'rb') as f:
                    img = Image.open(f)
                    img = img.convert('RGB')
                    img.thumbnail((512, 512), Image.LANCZOS)
                    buffer = BytesIO()
                    img.save(buffer, format='JPEG', quality=85, optimize=True)
                    new_filename = f"avatars/{username}.jpg"

                    # Delete old avatar file if it exists
                    if default_storage.exists(new_filename):
                        default_storage.delete(new_filename)

                    # Save processed image and update the field to point to the canonical filename
                    self.avatar.save(new_filename, ContentFile(buffer.getvalue()), save=False)
                    self.avatar.name = new_filename
                    buffer.close()

                # Remove other avatar files for this user
                avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
                for fname in os.listdir(avatar_dir):
                    if fname.startswith(username) and fname != f"{username}.jpg":
                        try:
                            os.remove(os.path.join(avatar_dir, fname))
                        except Exception:
                            pass

                super().save(update_fields=['avatar'])

class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    imageUrl = models.URLField(max_length=1024, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (by {self.user.username})"

class Channel(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='channels')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    imageUrl = models.URLField(max_length=1024, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (in {self.collection.name})"

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='bookmarks')
    video = models.ForeignKey('operations.Video', on_delete=models.CASCADE, related_name='bookmarks')
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    access = models.CharField(max_length=10, choices=ACCESS_CHOICES, default='public')
    tags = models.ManyToManyField('operations.Tag', blank=True, related_name='tagged_bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'channel', 'video')
        indexes = [
            models.Index(fields=['-created_at'], name='bm_created_at_desc_idx'),
            models.Index(fields=['video', 'access', 'created_at'], name='bm_vid_acc_crt_idx'),
            models.Index(fields=['user', 'created_at'], name='bm_usr_crt_idx'),
            models.Index(fields=['access', 'created_at'], name='bm_acc_crt_idx'),
        ]

    def __str__(self):
        return f"'{self.title}' bookmarked by {self.user.username} in '{self.channel.name}'"

class Notification(models.Model):
    """Model to store user notifications."""

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="The user who receives the notification."
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='actions_triggered',
        null=True,
        blank=True,
        help_text="The user who performed the action that triggered the notification."
    )
    verb = models.CharField(
        max_length=255,
        help_text="The verb describing the action (e.g., 'started following you', 'saved your bookmark')."
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='system',
        db_index=True
    )

    # --- Generic Foreign Keys for Flexibility ---
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, related_name='notification_target')
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    action_object_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, related_name='notification_action_object')
    action_object_object_id = models.PositiveIntegerField(null=True, blank=True)
    action_object = GenericForeignKey('action_object_content_type', 'action_object_object_id')

    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at'])
        ]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        if self.actor:
            if self.target:
                return f'{self.actor} {self.verb} {self.target}'
            else:
                return f'{self.actor} {self.verb}'
        else:
            return f'System: {self.verb}'

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

    def mark_as_unread(self):
        if self.is_read:
            self.is_read = False
            self.save(update_fields=['is_read'])

class Subscription(models.Model):
    """
    Model to manage user subscriptions, allowing for manual premium access.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='subscription',
        help_text="The user who has this subscription."
    )
    tier = models.CharField(
        max_length=50,
        choices=SUBSCRIPTION_TIER_CHOICES,
        default='premium',
        help_text="The subscription tier."
    )
    start_date = models.DateTimeField(
        help_text="The date and time when the subscription starts."
    )
    end_date = models.DateTimeField(
        help_text="The date and time when the subscription ends."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if the subscription is currently active. Can be manually overridden or determined by dates."
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Administrative notes about this subscription (e.g., reason for manual grant)."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-end_date', 'user__username']
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def __str__(self):
        return f"{self.user.username}'s {self.get_tier_display()} Subscription (Ends: {self.end_date.strftime('%Y-%m-%d')})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class MutedUser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='muter', on_delete=models.CASCADE)
    muted_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='muted', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'muted_user')
