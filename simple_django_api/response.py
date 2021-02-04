from http import HTTPStatus
from django.http.response import HttpResponse
from .compat import json


class APIResponse(HttpResponse):
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
        kwargs.setdefault('content_type', self.content_type)
        content = json.dumps(data, ensure_ascii=ensure_ascii)
        super().__init__(content=content, status=status_code, **kwargs)
