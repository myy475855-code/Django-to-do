from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """Object-level: only the owner may view/modify; admins may too."""
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_staff
