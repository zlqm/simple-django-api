import datetime
from http import HTTPStatus
import logging
import os

from django.urls import path
from django.core import management
from simple_django_api import exceptions, permissions, views

logger = logging.getLogger(__name__)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'app': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}


class Unauthorized(exceptions.APIError):
    status_code = HTTPStatus.UNAUTHORIZED


class BasicAuthRequired(permissions.BasePermission):
    def __call__(self):
        if not self.request.headers.get('Authorization'):
            raise Unauthorized(user_hint='basic_auth required')


class BasicAuthView(views.APIView):
    method_perms = {'GET': BasicAuthRequired}

    def get(self, request):
        return {'msg': 'hello world'}


class AuthView(views.APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return {'username': request.user.username}
        return {'username': None}


urlpatterns = [
    path('basic_auth', BasicAuthView.as_view()),
    path('auth', AuthView.as_view()),
]


def pytest_configure():
    import django
    from django.conf import settings

    settings.configure(
        ALLOWED_HOSTS='*',
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        SITE_ID=1,
        SECRET_KEY='not very secret in tests',
        STATIC_URL='/static/',
        ROOT_URLCONF=__name__,
        TEMPLATE_LOADERS=(
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ),
        MIDDLEWARE=(
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
            'simple_django_api.jwt.middleware.AuthenticationMiddleware',
        ),
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            #'tests',
        ),
        PASSWORD_HASHERS=('django.contrib.auth.hashers.MD5PasswordHasher', ),
        LOGGING=LOGGING,
        API_JWT_SECRET_KEY='some key',
        API_JWT_EXPIRATION_MINUTES=0.1,
    )

    import django
    django.setup()
    management.call_command('makemigrations')
    management.call_command('migrate')
