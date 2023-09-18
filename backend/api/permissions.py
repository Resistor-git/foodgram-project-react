from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Author has permission to create, update and delete the object.
    Others have permission to read (get) object.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)  # вторая часть or вообще нужна?

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin has permission to create, update and delete the object.
    Others have permission to read (get) object.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)  # нужно ли аутентификацию проверять? анонам тоже должно показывать?

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS  # не работает
                or request.user.is_staff)  # не уверен в этой строчке


class IsAuthenticatedOrListOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)  # нужно ли аутентификацию проверять? анонам тоже должно показывать?

    def has_object_permission(self, request, view, obj):
        return ((request.method in permissions.SAFE_METHODS and request.user.is_authenticated)  # не работает
                or request.user.is_staff)  # не уверен в этой строчке
