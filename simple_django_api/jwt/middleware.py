from django.utils.functional import SimpleLazyObject
from . import auth


def authenticate(request):
    user, jwt_info = auth.authenticate(request)
    request._cached_user = user
    request._jwt_info = jwt_info


def get_user(request):
    # other middleware may already set request._user
    if not hasattr(request, '_jwt_info'):
        authenticate(request)
    return request._cached_user


def get_jwt_info(request):
    if not hasattr(request, '_jwt_info'):
        authenticate(request)
    return request._jwt_info


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not hasattr(request, 'jwt_info'):
            request.user = SimpleLazyObject(lambda: get_user(request))
            request.jwt_info = SimpleLazyObject(lambda: get_jwt_info(request))
        response = self.get_response(request)
        return response
