from http import HTTPStatus
import logging

from django.conf import settings
from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

try:
    from webargs import ValidationError
except ImportError:
    from .exceptions import ValidationError

from .request import Request
from .response import APIResponse
from .utils.logging import LoggingContext


class APIView(View):
    method_perms = None
    logger = logging.getLogger(__name__)

    def _check_permission(self, request, **kwargs):
        default_perms = getattr(settings, 'API_DEFAULT_PERMS', [])
        method_perms = self.method_perms or {}
        perm_lst = method_perms.get(request.method.upper(), None)
        if perm_lst is None:
            perm_lst = method_perms.get(request.method.lower(), None)
        if perm_lst is None:
            perm_lst = default_perms
        if not isinstance(perm_lst, (list, tuple)):
            perm_lst = [perm_lst]
        for perm in perm_lst:
            perm_checker = perm(self)
            resp = perm_checker(request, **kwargs)
            if resp:
                return resp

    def _dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.request = request = Request(raw_request=request)
        try:
            resp = self._check_permission(request, **kwargs)
            if not resp:
                resp = self._dispatch(request, *args, **kwargs)
            if not isinstance(resp, HttpResponse):
                resp = APIResponse(resp)
            return resp
        except Exception as exc:
            exc_handler = getattr(settings, 'API_VIEW_EXCEPTION_HANDLER',
                                  self.exception_handler)
            return exc_handler(request, exc)

    def exception_handler(self, request, exc):
        options = {}
        if isinstance(exc, ValidationError):
            options['status_code'] = HTTPStatus.BAD_REQUEST
            options['user_hint'] = exc.messages
        self.log_exception(request, exc)
        return APIResponse.from_exception(exc, **options)

    def log_exception(self, request, exc):
        context = LoggingContext()
        context['method'] = request.method
        context['path'] = request.path
        context['query_params'] = request.query_params
        context['data'] = request.data
        context['user'] = str(request.user)
        context['exc'] = exc
        level = getattr(exc, 'logging_level', logging.ERROR)
        exc_info = level >= logging.ERROR
        self.logger.log(level, context, exc_info=exc_info)
