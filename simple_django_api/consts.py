from http import HTTPStatus

ERROR_MSG = {
    HTTPStatus.NOT_FOUND: 'not found',
    HTTPStatus.BAD_REQUEST: 'bad request',
    HTTPStatus.FORBIDDEN: 'permission denied',
    HTTPStatus.INTERNAL_SERVER_ERROR: 'internal server error',
}
