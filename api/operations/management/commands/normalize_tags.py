from django.core.management.base import BaseCommand
from django.db import transaction
from operations.models import Tag
from operations.utils import normalize_tag_name


class Command(BaseCommand):
    help = 'Clean up and normalize existing tags in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        # Find tags that need normalization
        tags_to_fix = []
        all_tags = Tag.objects.all()
        
        for tag in all_tags:
            normalized = normalize_tag_name(tag.name)
            if tag.name != normalized:
                tags_to_fix.append((tag, normalized))
        
        if not tags_to_fix:
            self.stdout.write(
                self.style.SUCCESS('No tags need normalization!')
            )
            return
        
        self.stdout.write(f'Found {len(tags_to_fix)} tags that need normalization:')
        
        for tag, normalized in tags_to_fix:
            self.stdout.write(f'  "{tag.name}" -> "{normalized}"')
        
        if dry_run:
            return
        
        # Perform the normalization
        with transaction.atomic():
            for tag, normalized in tags_to_fix:
                # Check if normalized tag already exists
                existing = Tag.objects.filter(name=normalized).exclude(id=tag.id).first()
                
                if existing:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Merging "{tag.name}" into existing "{normalized}"'
                        )
                    )
                    
                    # Move all relationships to the existing normalized tag
                    # Videos
                    for video in tag.videos.all():
                        video.tags.remove(tag)
                        video.tags.add(existing)
                    
                    # Bookmarks  
                    for bookmark in tag.tagged_bookmarks.all():
                        bookmark.tags.remove(tag)
                        bookmark.tags.add(existing)
                    
                    # Delete the old tag
                    tag.delete()
                    
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'Normalizing "{tag.name}" to "{normalized}"')
                    )
                    # Just update the name
                    tag.name = normalized
                    tag.save()
        
        self.stdout.write(
            self.style.SUCCESS('Tag normalization completed!')
        )
