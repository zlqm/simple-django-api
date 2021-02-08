import logging
from http import HTTPStatus
from .errors import ERROR_MSG


class APIError(Exception):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    logging_level = logging.ERROR

    def __init__(self,
                 *,
                 user_hint='',
                 logging_hint='',
                 status_code=None,
                 logging_level=None):
        cls = self.__class__
        self.user_hint = user_hint or ERROR_MSG.get(status_code, f'')
        self.logging_hint = logging_hint or self.user_hint
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
    logging_level = logging.ERROR


class ParamsError(APIError):
    status_code = HTTPStatus.BAD_REQUEST
    logging_level = logging.WARNING


class ValidationError(ParamsError):
    messages = ERROR_MSG.get(HTTPStatus.UNPROCESSABLE_ENTITY)


class Unauthorized(APIError):
    status_code = HTTPStatus.UNAUTHORIZED
    logging_level = logging.WARNING


class Forbidden(APIError):
    status_code = HTTPStatus.FORBIDDEN
    logging_level = logging.WARNING


class NotFound(APIError):
    status_code = HTTPStatus.NOT_FOUND
    logging_level = logging.WARNING
