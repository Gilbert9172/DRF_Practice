# 권한 커스텀.
from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """본인만 접근 가능"""
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
