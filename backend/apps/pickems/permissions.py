from rest_framework.permissions import BasePermission

from apps.pickems.choices import GroupRole

class IsPickemGroupMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.memberships.filter(user=request.user).exists()

class IsPickemGroupOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        membership = obj.memberships.filter(user=request.user).first()
        return bool(membership and membership.role == GroupRole.OWNER)