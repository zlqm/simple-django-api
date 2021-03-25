from http import HTTPStatus
from django.http.response import HttpResponse

from . import consts, compat, exceptions


class JsonResponse(HttpResponse):
    """HTTP Response in json format
    """
    content_type = 'application/json'

    def __init__(self,
                 data,
                 *,
                 ensure_ascii=False,
                 status_code=HTTPStatus.OK,
                 **kwargs):
        if isinstance(data, str):
            data = {'detail': data}
        if hasattr(status_code, 'value'):
            status_code = status_code.value
        kwargs['content_type'] = self.content_type
        content = compat.json.dumps(data, ensure_ascii=ensure_ascii)
        super().__init__(content=content, status=status_code, **kwargs)

    @classmethod
    def from_exception(cls,
                       exc: exceptions.APIError,
                       status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                       user_hint=''):
        """Generate response from APIError
        """
        if not user_hint:
            user_hint = getattr(exc, 'user_hint', '')
        if not user_hint:
            user_hint = consts.ERROR_MSG.get(status_code, '')
        status_code = getattr(exc, 'status_code', status_code)
        return cls(user_hint, status_code=status_code)

    @classmethod
    def created(cls, data, **kwargs):
        kwargs['status_code'] = HTTPStatus.CREATED
        return cls(data, **kwargs)

    @classmethod
    def not_found(cls, data, **kwargs):
        kwargs['status_code'] = HTTPStatus.NOT_FOUND
        return cls(data, **kwargs)


APIResponse = JsonResponse
