import logging

from django.views import View
from django.conf import settings
from .request import Request
from .response import APIResponse

logger = logging.getLogger('django_improved_view.view_error')


def view_exception_handler(request, exc):
    context = {
        'path': request.path,
        'method': request.method,
        'user': request.user,
        'query_params': request.query_params,
        'data': request.data
    }
    log_level = getattr(exc, 'LOG_LEVEL', logging.ERROR)
    extra_option = {}
    if log_level >= logging.ERROR:
        extra_option['exc_info'] = True
    context['exc'] = getattr(exc, 'log_hint', str(exc))
    log_content = ' '.join('[{}: {}]'.format(key, value)
                           for key, value in context.items())
    logger.log(log_level, log_content, **extra_option)
    if hasattr(exc, 'error_code'):
        hint = getattr(exc, 'user_hint', '')
        status_code = getattr(exc, 'http_status_code', 200)
        return APIResponse(dict(),
                           error_code=exc.error_code,
                           hint=hint,
                           status=status_code)
    return APIResponse.internal_error()


class APIView(View):
    default_perms = getattr(settings, 'IMPROVED_VIEW_PERMS', [])
    # different method may need different perm
    method_perms = {}

    def check_permission(self):
        perm_lst = self.method_perms.get(self.request.method,
                                         self.default_perms)
        if not isinstance(perm_lst, (list, tuple)):
            perm_lst = [perm_lst]
        for perm in perm_lst:
            perm_checker = perm(self.request, self)
            perm_checker()

    def dispatch(self, request, *args, **kwargs):
        request = self.request = Request(request)
        try:
            self.check_permission()
            return super().dispatch(self.request, *args, **kwargs)
        except Exception as err:
            exc_handler = getattr(settings, 'IMPROVED_VIEW_EXCEPTION_HANDLER',
                                  view_exception_handler)
            return exc_handler(request, err)
