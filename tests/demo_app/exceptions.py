from http import HTTPStatus
from simple_django_api.exceptions import APIError


class Unauthorized(APIError):
    status_code = HTTPStatus.UNAUTHORIZED
