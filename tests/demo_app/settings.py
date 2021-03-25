"""settings for demo app
"""
ALLOWED_HOSTS = '*'
DEBUG_PROPAGATE_EXCEPTIONS = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}
SITE_ID = 1
SECRET_KEY = 'not very secret in tests'
STATIC_URL = '/static/'
ROOT_URLCONF = 'tests.demo_app.urls'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_django_api.jwt.middleware.AuthenticationMiddleware',
)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)
PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher', )
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
API_JWT_SECRET_KEY = 'some key'
API_JWT_EXPIRATION_MINUTES = 0.05
