# 권한 커스텀.
from rest_framework.permissions import BasePermission
from django.contrib import auth

class IsOwner(BasePermission):
    """본인만 접근 가능"""
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class OnlyOwner(BasePermission):
    """본인만 조회 가능"""
    def has_permission(self, request, view):
        owner = request.user.username
        username = request.query_params.get('username')
        return owner==username


# 포스팅 올리는 사람이 본인 + 증명
# class PostOwner(BasePermission):
#     def has_permission(self, request, view):
#         request_user = request.user
        