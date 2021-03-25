from datetime import datetime, timedelta
from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.utils.functional import SimpleLazyObject
import jwt

from .settings import settings
from .consts import TokenCase


def get_user(user_pk=None):
    """
    Return the user model instance associated with the given pk.
    If no user is retrieved, return an instance of `AnonymousUser`.
    """
    from django.contrib.auth.models import AnonymousUser
    user = None
    if user_pk:
        user = get_user_model().objects.filter(pk=user_pk).first()
    return user or AnonymousUser()


@dataclass
class JwtConfig:
    key: str
    algorithm: str
    verify_exp: bool
    auth_cookie: str
    expiration_minutes: (float, int)
    user_pk_key: str


def get_jwt_config():
    return JwtConfig(
        key=settings.API_JWT_SECRET_KEY,
        algorithm=settings.API_JWT_ALGORITHM,
        verify_exp=settings.API_JWT_VERIFY_EXPIRATION,
        auth_cookie=settings.API_JWT_AUTH_COOKIE,
        expiration_minutes=settings.API_JWT_EXPIRATION_MINUTES,
        user_pk_key='sub',
    )


JWT_CONFIG = SimpleLazyObject(get_jwt_config)


def encode(payload: dict) -> str:
    """Accept payload and generate token string
    """
    return jwt.encode(payload, JWT_CONFIG.key,
                      JWT_CONFIG.algorithm).decode('utf8')


def decode(token: str) -> dict:
    """receive token and get payload
    """
    options = {'verify_exp': JWT_CONFIG.verify_exp}
    return jwt.decode(
        token,
        JWT_CONFIG.key,
        options=options,
        algorithms=[JWT_CONFIG.algorithm],
    )


def get_token_from_request(request):
    """get token string from request
    token may stored in cookie or header `AUTHORIZATION`
    """
    if JWT_CONFIG.auth_cookie:
        authorization = request.COOKIES.get(JWT_CONFIG.auth_cookie, b'')
    else:
        authorization = request.META.get('HTTP_AUTHORIZATION', b'')
    if hasattr(authorization, 'decode'):
        try:
            authorization = authorization.decode()
        except UnicodeDecodeError:
            return None, 'decode error'
    auth = authorization.split()
    if len(auth) == 2 and auth[0].lower() == 'bearer':
        return auth[1], ''
    return None, 'bad format'


def generate_token(user):
    """generate token for user
    """
    delta = timedelta(minutes=JWT_CONFIG.expiration_minutes)
    expire_at = datetime.utcnow() + delta
    payload = {'exp': expire_at, JWT_CONFIG.user_pk_key: user.pk}
    return encode(payload)


def authenticate(request):
    """Return the user model instance associated with the given request
    If no user is retrieved, return an instance of `AnonymousUser`
    """
    token, _ = get_token_from_request(request)
    jwt_info = {
        'token': token,
        'case': TokenCase.OK,
        'payload': None,
    }
    if not token:
        jwt_info['case'] = TokenCase.NO_TOKEN
        return get_user(), jwt_info
    try:
        payload = decode(token)
        user_pk = payload[JWT_CONFIG.user_pk_key]
        return get_user(user_pk=user_pk), jwt_info
    except jwt.ExpiredSignature:
        jwt_info['case'] = TokenCase.EXPIRED
    except jwt.DecodeError:
        jwt_info['case'] = TokenCase.DECODE_ERROR
    except jwt.InvalidTokenError:
        jwt_info['case'] = TokenCase.INVALID_TOKEN
    except KeyError:
        jwt_info['case'] = TokenCase.MISSING_KEY
    return get_user(), jwt_info
