from rest_framework.permissions import BasePermission

class IsModeratorPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST' and request.user.is_staff:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.owner == request.user  