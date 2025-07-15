"""
Utility functions for tag handling
"""

def normalize_tag_name(tag_name):
    """
    Normalize a tag name to match the Tag model's save method.
    Converts to lowercase, removes spaces, and strips whitespace.
    """
    if not tag_name:
        return ''
    return tag_name.lower().replace(' ', '').strip()

def create_or_get_tags(tag_names):
    """
    Create or get Tag objects for a list of tag names.
    Returns a list of Tag objects with normalized names.
    """
    from operations.models import Tag
    
    tag_objs = []
    for tag_name in tag_names:
        normalized_name = normalize_tag_name(tag_name)
        if normalized_name:  # Only create non-empty tags
            tag, _ = Tag.objects.get_or_create(name=normalized_name)
            tag_objs.append(tag)
    return tag_objs
