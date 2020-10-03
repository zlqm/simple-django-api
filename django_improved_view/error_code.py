from http import HTTPStatus

# user can rewrite value via
# > from .? import error_code
# > error_code.INTERNAL_SERVER = 1000
# > error_code.BAD_REQUEST = 1001
OK = HTTPStatus.OK.value
INTERNAL_SERVER_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR.value
BAD_REQUEST = HTTPStatus.BAD_REQUEST.value
UNAUTHORIZED = HTTPStatus.UNAUTHORIZED.value
FORBIDDEN = HTTPStatus.FORBIDDEN.value
NOT_FOUND = HTTPStatus.NOT_FOUND.value
