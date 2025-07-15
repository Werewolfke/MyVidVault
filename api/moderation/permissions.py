from rest_framework import permissions

class IsModerator(permissions.BasePermission):
    """
    Allows access only to users with is_moderator=True in their profile.
    """
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'profile') and request.user.profile.is_moderator)
