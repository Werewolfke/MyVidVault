from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Profile, Collection, Channel


class Command(BaseCommand):
    help = 'Create missing profiles for existing users'

    def handle(self, *args, **options):
        users_without_profiles = User.objects.filter(profile__isnull=True)
        
        if not users_without_profiles.exists():
            self.stdout.write(
                self.style.SUCCESS('All users already have profiles.')
            )
            return

        created_count = 0
        for user in users_without_profiles:
            # Create profile
            profile = Profile.objects.create(user=user)
            
            # Create default collection if the user doesn't have one
            if not user.collections.exists():
                collection = Collection.objects.create(
                    user=user,
                    name=user.username,
                    description=f"{user.username}'s collection"
                )
                # Create default channel
                Channel.objects.create(
                    collection=collection,
                    name=f"{user.username}'s channel",
                    description=f"Default channel for {user.username}"
                )
            
            created_count += 1
            self.stdout.write(f'Created profile for user: {user.username}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} profiles.'
            )
        )
