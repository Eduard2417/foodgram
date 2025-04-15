from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    '''Уровень доступа для автора или только для чтения'''

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                or request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return (request.user == obj.author
                or request.method in permissions.SAFE_METHODS)
