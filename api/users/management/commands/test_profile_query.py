from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Profile
from users.views import UserProfileView

class Command(BaseCommand):
    help = 'Test the optimized profile query'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to test')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            # Test the optimized view
            view = UserProfileView()
            view.kwargs = {'username': username}
            
            self.stdout.write(f"Testing profile query for user: {username}")
            
            profile = view.get_object()
            
            self.stdout.write(self.style.SUCCESS(f"✓ Successfully retrieved profile for {username}"))
            self.stdout.write(f"  - Followers: {getattr(profile, '_followers_count', 'N/A')}")
            self.stdout.write(f"  - Following: {getattr(profile, '_following_count', 'N/A')}")
            self.stdout.write(f"  - Bookmarks: {getattr(profile, '_bookmarks_count', 'N/A')}")
            self.stdout.write(f"  - Likes: {getattr(profile, '_likes_count', 'N/A')}")
            self.stdout.write(f"  - Collections: {len(getattr(profile, '_prefetched_collections', []))}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error: {str(e)}"))
