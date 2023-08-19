from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Author has permission to create, update and delete the object.
    Others have permission to read (get) object.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
