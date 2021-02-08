from http import HTTPStatus

from .response import APIResponse

ERROR_MSG = {
    HTTPStatus.NOT_FOUND: 'not found',
    HTTPStatus.BAD_REQUEST: 'bad request',
    HTTPStatus.FORBIDDEN: 'permission denied',
    HTTPStatus.INTERNAL_SERVER_ERROR: 'internal server error',
}


def api_error(status_code):
    msg = ERROR_MSG.get(status_code, '')
    return APIResponse(msg, status_code=status_code)


def page_not_found(request, exc=None, **kwargs):
    return api_error(HTTPStatus.NOT_FOUND)


def unauthorized(request, exc=None, **kwargs):
    return api_error(HTTPStatus.UNAUTHORIZED)


def bad_reqeust(request, exc=None, **kwargs):
    return api_error(HTTPStatus.BAD_REQUEST)


def permission_denied(request, exc=None, **kwargs):
    return api_error(HTTPStatus.FORBIDDEN)


def server_error(request, **kwargs):
    return api_error(HTTPStatus.INTERNAL_SERVER_ERROR)
