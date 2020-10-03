from io import BytesIO
from types import MethodType
from .compat import complex_json

from django.core.handlers.wsgi import WSGIRequest as OriginWSGIRequest
from django.http.request import HttpRequest, QueryDict
from django.http.multipartparser import MultiPartParserError
from django.utils.datastructures import MultiValueDict

from . import exceptions


def parse_json_body(input_data, *, encoding=None):
    encoding = encoding or 'utf8'
    try:
        if hasattr(input_data, 'decode'):
            input_data = input_data.decode(encoding)
        return complex_json.loads(input_data)
    except (complex_json.JSONDecodeError, ValueError):
        raise exceptions.InvalidRequestBody(
            'failed to load application/json: %s' % input_data)


def _load_post_and_files(self):
    # 这里的代码直接拷贝的Django代码，
    # 如果未来Django调整内部实现，本方法就不能用了
    if self.method.upper() not in ('POST', 'PUT', 'PATCH'):
        self._post = QueryDict(encoding=self._encoding)
        self._files = MultiValueDict()
        return
    if self._read_started and not hasattr(self, '_body'):
        self._mark_post_parse_error()
        return

    if self.content_type == 'multipart/form-data':
        if hasattr(self, '_body'):
            # Use already read data
            data = BytesIO(self._body)
        else:
            data = self
        try:
            self._post, self._files = self.parse_file_upload(self.META, data)
        except MultiPartParserError:
            # An error occurred while parsing POST data. Since when
            # formatting the error the request handler might access
            # self.POST, set self._post and self._file to prevent
            # attempts to parse POST data again.
            # Mark that an error occurred. This allows self.__repr__ to
            # be explicit about it instead of simply representing an
            # empty POST
            self._mark_post_parse_error()
            raise
    elif self.content_type == 'application/x-www-form-urlencoded':
        self._post = QueryDict(self.body, encoding=self._encoding)
        self._files = MultiValueDict()
    elif self.content_type == 'application/json':
        self._post = parse_json_body(self.body, encoding=self._encoding)
        self._files = MultiValueDict()
    else:
        self._post = QueryDict(encoding=self._encoding)
        self._files = MultiValueDict()


class Request:
    """对Django原有Request进行封装，主要添加json body的解析功能
    """
    METHODS_WITH_PAYLOAD = ['POST', 'PATCH', 'PUT']

    def __init__(self, raw_request=None):
        if not raw_request:
            raw_request = HttpRequest()
        raw_request._load_post_and_files = MethodType(_load_post_and_files,
                                                      raw_request)
        self._raw_request = raw_request

    @property
    def data(self):
        return self._raw_request.POST

    @property
    def query_params(self):
        return self._raw_request.GET

    def __repr__(self):
        return repr(self._raw_request)

    def __getattr__(self, name):
        return getattr(self._raw_request, name)

    def __setattr__(self, name, value):
        name_list = ['_raw_request', '_data']
        if name in name_list:
            super().__setattr__(name, value)
        else:
            return setattr(self._raw_request, name, value)

    def __iter__(self):
        return iter(self._raw_request)


class WSGIRequest(Request):
    def __init__(self, environ, raw_request=None):
        if not raw_request:
            raw_request = OriginWSGIRequest(environ)
        super().__init__(raw_request=raw_request)

    def __repr__(self):
        return repr(self._raw_request)
