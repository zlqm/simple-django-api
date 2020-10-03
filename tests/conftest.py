import datetime
import logging
import os

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
        'django_improved_view': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}


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
        ROOT_URLCONF='tests.urls',
        TEMPLATE_LOADERS=(
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ),
        MIDDLEWARE=('django.middleware.security.SecurityMiddleware',
                    'django.contrib.sessions.middleware.SessionMiddleware',
                    'django.middleware.common.CommonMiddleware',
                    'django.middleware.csrf.CsrfViewMiddleware',
                    'django.contrib.auth.middleware.AuthenticationMiddleware',
                    'django.contrib.messages.middleware.MessageMiddleware',
                    'django.middleware.clickjacking.XFrameOptionsMiddleware'),
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'tests',
        ),
        PASSWORD_HASHERS=('django.contrib.auth.hashers.MD5PasswordHasher', ),
        # JWT_EXPIRATION_DELTA=datetime.timedelta(seconds=2),
        LOGGING=LOGGING,
    )

    try:
        import oauth_provider    # NOQA
        import oauth2    # NOQA
    except ImportError:
        pass
    else:
        settings.INSTALLED_APPS += ('oauth_provider', )

    try:
        if django.VERSION >= (1, 8):
            # django-oauth2-provider does not support Django1.8
            raise ImportError
        import provider    # NOQA
    except ImportError:
        pass
    else:
        settings.INSTALLED_APPS += (
            'provider',
            'provider.oauth2',
        )

    import django
    django.setup()
