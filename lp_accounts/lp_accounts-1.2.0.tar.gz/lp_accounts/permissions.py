from rest_framework import permissions


class IsAnonUser(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return not super(IsAnonUser, self).has_permission(request, view)
