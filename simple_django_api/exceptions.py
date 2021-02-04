import logging
from http import HTTPStatus


class APIError(Exception):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    user_hint = 'internal error'
    logging_hint = 'internal error'
    logging_level = logging.ERROR

    def __init__(self,
                 *,
                 user_hint='',
                 logging_hint='',
                 status_code=None,
                 logging_level=None):
        cls = self.__class__
        self.user_hint = user_hint or cls.user_hint
        self.logging_hint = logging_hint or user_hint or cls.logging_hint
        self.status_code = status_code or cls.status_code
        self.logging_level = logging_level or cls.logging_level

    def __str__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}: {self.user_hint}'

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}: {self.logging_hint}'


class InternalError(APIError):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    user_hint = 'internal error'
    logging_hint = 'internal error'
    logging_level = logging.ERROR


class ParamsError(APIError):
    status_code = HTTPStatus.BAD_REQUEST
    user_hint = 'bad request'
    logging_hint = 'bad request'
    logging_level = logging.WARNING


class Unauthorized(APIError):
    status_code = HTTPStatus.UNAUTHORIZED
    user_hint = 'unauthorized'
    logging_hint = 'unauthorized'
    logging_level = logging.WARNING


class Forbidden(APIError):
    status_code = HTTPStatus.FORBIDDEN
    user_hint = 'forbidden'
    logging_hint = 'forbidden'
    logging_level = logging.WARNING


class NotFound(APIError):
    status_code = HTTPStatus.NOT_FOUND
    user_hint = 'not found'
    logging_hint = 'not found'
    logging_level = logging.WARNING
