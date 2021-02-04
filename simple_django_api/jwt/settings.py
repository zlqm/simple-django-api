from simple_django_api.utils import SettingsProxy

settings = SettingsProxy(
    API_JWT_ALGORITHM='HS256',
    API_JWT_AUTH_COOKIE='',
    API_JWT_VERIFY_EXPIRATION=True,
    API_JWT_EXPIRATION_MINUTES=10,
)
