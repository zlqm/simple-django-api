from django.conf.urls import url

from django_improved_view import exceptions, permissions
from django_improved_view.response import APIResponse
from django_improved_view.views import APIView
from django_improved_view.permissions import BasePermission

import logging


class BasicAuthRequiredError(exceptions.APIException):
    HTTP_STATUS_CODE = 401
    ERROR_CODE = 10000


class TokenRequired(BasePermission):
    def __call__(self):
        if not self.request.headers.get('Authorization'):
            raise BasicAuthRequiredError(user_hint='basic auth required')


class PermissionView(APIView):
    method_perms = {'GET': [TokenRequired]}

    def get(self, request):
        return APIResponse.ok({})


urlpatterns = [
    url('perm-test', PermissionView.as_view()),
]
