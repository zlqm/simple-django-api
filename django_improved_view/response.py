from django.http.response import HttpResponse

from . import error_code
from .compat import complex_json


class APIResponse(HttpResponse):
    content_type = 'application/json'

    def __init__(self,
                 content,
                 *,
                 error_code=error_code.OK,
                 hint='',
                 ensure_ascii=False,
                 **kwargs):
        data = {'error_code': error_code, 'hint': hint, 'data': content}
        if 'content_type' not in kwargs:
            kwargs['content_type'] = self.content_type
        content = complex_json.dumps(data, ensure_ascii=ensure_ascii)
        super().__init__(content=content, **kwargs)

    @classmethod
    def internal_error(cls,
                       error_code=error_code.INTERNAL_SERVER_ERROR,
                       **kwargs):
        return cls({}, error_code=error_code, **kwargs)

    @classmethod
    def ok(cls, content, **kwargs):
        return cls(content, **kwargs)
