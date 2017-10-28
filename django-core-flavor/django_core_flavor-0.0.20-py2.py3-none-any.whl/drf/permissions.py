from rest_framework import permissions


class IsStaffList(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action == 'list' and request.user is not None:
            return request.user.is_staff
        return True
