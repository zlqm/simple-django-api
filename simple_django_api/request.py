from io import BytesIO
from types import MethodType

from django.core.handlers.wsgi import WSGIRequest as OriginWSGIRequest
from django.http.request import HttpRequest, QueryDict
from django.http.multipartparser import MultiPartParserError
from django.utils.datastructures import MultiValueDict

from . import compat, exceptions


def parse_json_body(input_data, *, encoding=None):
    encoding = encoding or 'utf8'
    try:
        if hasattr(input_data, 'decode'):
            input_data = input_data.decode(encoding)
        return compat.json.loads(input_data)
    except (compat.json.JSONDecodeError, ValueError):
        raise exceptions.InvalidRequestBody()


# this code is part of django.http.request.HttpRequest
def _load_post_and_files(self):
    """Populate self._post and self._files if the content-type is a form type"""
    if self.method not in ['POST', 'PUT', 'PATCH']:
        self._post, self._files = QueryDict(
            encoding=self._encoding), MultiValueDict()
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
            self._mark_post_parse_error()
            raise
    elif self.content_type == 'application/x-www-form-urlencoded':
        self._post, self._files = QueryDict(
            self.body, encoding=self._encoding), MultiValueDict()
    elif self.content_type == 'application/json':
        self._post = parse_json_body(self.body, encoding=self._encoding)
        self._files = MultiValueDict()
    else:
        self._post, self._files = QueryDict(
            encoding=self._encoding), MultiValueDict()


class Request:
    def __init__(self, raw_request=None):
        if raw_request is None:
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

    @property
    def files(self):
        return self._raw_request.files

    def __getattr__(self, name):
        return getattr(self._raw_request, name)

    def __setattr__(self, name, value):
        key_lst = {
            '_raw_request',
        }
        if name in key_lst:
            super().__setattr__(name, value)
        else:
            setattr(self._raw_request, name, value)

    def __repr__(self):
        return repr(self._raw_request)

    def __iter__(self):
        return iter(self._raw_request)


class WSGIRequest(Request):
    def __init__(self, environ, raw_request=None):
        if not raw_request:
            raw_request = OriginWSGIRequest(environ)
        super().__init__(raw_request=raw_request)

    def __repr__(self):
        return repr(self._raw_request)
