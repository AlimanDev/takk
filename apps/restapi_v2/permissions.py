from rest_framework import permissions
from apps.users import models as user_models


class IsEmployee(permissions.BasePermission):

    def has_permission(self, request, view):
        return not request.user.user_type == user_models.User.USER


class IsCompanyOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.user_type == user_models.User.COMPANY_OWNER and request.user.phone_is_verified

