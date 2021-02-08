from http import HTTPStatus
import logging

from django.conf import settings
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

try:
    from webargs import ValidationError
except ImportError:
    from .exceptions import ValidationError

from . import errors
from .exceptions import Unauthorized
from .request import Request
from .response import APIResponse

logger = logging.getLogger(__name__)


class APIView(View):
    method_perms = {}
    logger = logger

    def _check_permission(self, request):
        default_perms = getattr(settings, 'API_DEFAULT_PERMS', [])
        perm_lst = self.method_perms.get(request.method.upper(), None)
        if perm_lst is None:
            perm_lst = self.method_perms.get(request.method.lower(), None)
        if perm_lst is None:
            perm_lst = default_perms
        if not isinstance(perm_lst, (list, tuple)):
            perm_lst = [perm_lst]
        for perm in perm_lst:
            perm_checker = perm(request, self)
            perm_checker()

    def _dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.request = request = Request(raw_request=request)
        try:
            self._check_permission(request)
            resp = self._dispatch(request, *args, **kwargs)
            if isinstance(resp, (str, dict, list)):
                resp = APIResponse(resp)
            return resp
        except Exception as exc:
            exc_handler = getattr(settings, 'API_VIEW_EXCEPTION_HANDLER',
                                  self.exception_handler)
            return exc_handler(request, exc)

    def exception_handler(self, request, exc):
        if isinstance(exc, ValidationError):
            return APIResponse(exc.messages,
                               status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
        self.log_exception(request, exc)

        msg = getattr(exc, 'user_hint', 'internal_error')
        status_code = getattr(exc, 'status_code',
                              HTTPStatus.INTERNAL_SERVER_ERROR)
        return APIResponse(msg, status_code=status_code)

    def log_exception(self, request, exc):
        context = {
            'method': request.method,
            'path': request.path,
            'query_params': request.query_params,
            'data': request.data,
        }
        try:
            context['user'] = request.user
            request.user.is_authenticated  # user is lazy object
        except Exception:
            # must import after django setup
            from django.contrib.auth.models import AnonymousUser
            context['user'] = AnonymousUser
        context['exc'] = exc
        level = getattr(exc, 'logging_level', logging.ERROR)
        extra_option = {}
        if level >= logging.ERROR:
            extra_option['exc_info'] = True
        log_content = ' '.join(f'[{key}: {value}]'
                               for key, value in context.items())
        self.logger.log(level, log_content, **extra_option)
