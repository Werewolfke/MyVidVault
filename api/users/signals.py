from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Collection, Channel

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        # Create a Collection with the user's username
        collection = Collection.objects.create(
            user=instance,
            name=instance.username,
            description=f"{instance.username}'s collection"
        )
        # Create a Channel in that Collection
        Channel.objects.create(
            collection=collection,
            name=f"{instance.username}'s channel",
            description=f"Default channel for {instance.username}"
        )