from datetime import datetime, timedelta
import logging

from django.contrib.auth import get_user_model
import jwt

from simple_django_api.exceptions import Unauthorized

from .settings import settings

logger = logging.getLogger(__name__)


def jwt_encode_handler(payload):
    key = settings.API_JWT_SECRET_KEY
    algorithm = settings.API_JWT_ALGORITHM
    return jwt.encode(payload, key, algorithm).decode('utf8')


def jwt_decode_handler(token):
    options = {
        'verify_exp': settings.API_JWT_VERIFY_EXPIRATION,
    }
    return jwt.decode(token,
                      settings.API_JWT_SECRET_KEY,
                      options=options,
                      algorithms=[settings.API_JWT_ALGORITHM])


def get_jwt_value(request):
    '''there are two ways to provide token
    1. Header AUTHORIZATION
    2. Cookie
    '''
    if settings.API_JWT_AUTH_COOKIE:
        authorization = request.COOKIES.get(settings.API_JWT_AUTH_COOKIE)
    else:
        authorization = request.META.get('HTTP_AUTHORIZATION', b'')
    if hasattr(authorization, 'decode'):
        try:
            authorization = authorization.decode()
        except UnicodeDecodeError:
            return None, 'decode error'
    auth = authorization.split()
    if len(auth) == 2 and auth[0].lower() == 'bearer':
        return auth[1], 'ok'
    return None, 'bad format'


def authenticate(jwt_value):
    if not jwt_value:
        return None
    try:
        payload = jwt_decode_handler(jwt_value)
        return payload['sub']
    except jwt.ExpiredSignature:
        msg = 'Signature has expired.'
        raise Unauthorized(user_hint=msg)
    except jwt.DecodeError:
        msg = 'Error decoding signature.'
        raise Unauthorized(user_hint=msg)
    except jwt.InvalidTokenError:
        raise Unauthorized(user_hint='bad request')
    except KeyError:
        raise Unauthorized(user_hint='bad request')


def genereate_token(user):
    delta = timedelta(minutes=settings.API_JWT_EXPIRATION_MINUTES)
    expire_at = datetime.utcnow() + delta
    payload = {'exp': expire_at, 'sub': user.pk}
    return jwt_encode_handler(payload)


def get_user(request):
    """
    Return the user model instance associated with the given request session.
    If no user is retrieved, return an instance of `AnonymousUser`.
    """
    from django.contrib.auth.models import AnonymousUser

    jwt_value, _ = get_jwt_value(request)
    user_pk = authenticate(jwt_value)
    User = get_user_model()
    user = User.objects.filter(pk=user_pk).first()
    return user or AnonymousUser()
