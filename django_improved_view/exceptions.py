import logging
from http import HTTPStatus

from . import error_code


class APIException(Exception):
    HTTP_STATUS_CODE = HTTPStatus.INTERNAL_SERVER_ERROR.value
    ERROR_CODE = error_code.INTERNAL_SERVER_ERROR
    USER_HINT = 'internal error'
    LOG_HINT = 'internal error'
    LOG_LEVEL = logging.ERROR

    def __init__(self,
                 *,
                 user_hint=None,
                 log_hint=None,
                 error_code=None,
                 http_status_code=None):
        self.error_code = error_code or self.ERROR_CODE
        self.user_hint = user_hint or self.USER_HINT
        self.log_hint = log_hint or self.LOG_HINT
        self.http_status_code = http_status_code or self.HTTP_STATUS_CODE


class BAD_REQUEST(APIException):
    HTTP_STATUS_CODE = HTTPStatus.BAD_REQUEST.value
    ERROR_CODE = error_code.BAD_REQUEST
    USER_HINT = 'invalid request body'
    LOG_HINT = 'invalid request body'


class ParamsError(APIException):
    HTTP_STATUS_CODE = HTTPStatus.BAD_REQUEST.value
    ERROR_CODE = error_code.BAD_REQUEST
    USER_HINT = 'invalid request params'
    LOG_HINT = 'invalid request params'


class Unauthorized(APIException):
    HTTP_STATUS_CODE = HTTPStatus.UNAUTHORIZED.value
    ERROR_CODE = error_code.UNAUTHORIZED
    USER_HINT = 'unauthorized'
    LOG_HINT = 'unauthorized'


class Forbidden(APIException):
    HTTP_STATUS_CODE = HTTPStatus.FORBIDDEN.value
    ERROR_CODE = error_code.FORBIDDEN
    USER_HINT = 'permission denied'
    LOG_HINT = 'permission denied'


class NotFound(APIException):
    HTTP_STATUS_CODE = HTTPStatus.NOT_FOUND.value
    ERROR_CODE = error_code.NOT_FOUND
    USER_HINT = 'not found'
    LOG_HINT = 'not found'
