from simple_django_api import permissions
from simple_django_api.response import APIResponse
from simple_django_api.jwt.consts import TokenCase
from .exceptions import Unauthorized


class BasicAuthRequired(permissions.BasePermission):
    def __call__(self, request):
        if not request.headers.get('Authorization'):
            raise Unauthorized(user_hint='basic_auth required')


def login_required(view_cls):
    def inner(request):
        if not request.user.is_authenticated:
            raise Unauthorized(user_hint=request.jwt_info['case'].name)

    return inner


def owner_required(view_cls):
    def inner(request, pk=None, **kwargs):
        if pk != 1:
            return APIResponse('not owner')

    return inner
