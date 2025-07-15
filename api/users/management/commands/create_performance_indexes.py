from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Add performance indexes for user profile queries'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        
        indexes_to_create = [
            # Index for Follow table - followers count
            "CREATE INDEX IF NOT EXISTS idx_follow_followed_user ON users_follow(followed_id);",
            
            # Index for Follow table - following count  
            "CREATE INDEX IF NOT EXISTS idx_follow_follower_user ON users_follow(follower_id);",
            
            # Index for Bookmark table - user bookmarks count
            "CREATE INDEX IF NOT EXISTS idx_bookmark_user ON users_bookmark(user_id);",
            
            # Index for VideoLike table - user likes count (if exists)
            "CREATE INDEX IF NOT EXISTS idx_videolike_user ON operations_videolike(user_id);",
            
            # Composite index for collections with user
            "CREATE INDEX IF NOT EXISTS idx_collection_user_created ON users_collection(user_id, created_at DESC);",
            
            # Composite index for channels with collection
            "CREATE INDEX IF NOT EXISTS idx_channel_collection ON users_channel(collection_id);",
        ]
        
        for index_sql in indexes_to_create:
            try:
                cursor.execute(index_sql)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created index: {index_sql.split()[5]}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Index creation failed or already exists: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Performance indexes creation completed!')
        )
