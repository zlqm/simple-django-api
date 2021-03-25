"""
You can writer permission in two ways:

.. code:: python

    class LoginRequired:
        def __init__(self, view_cls):
            self.view_cls = view_cls

        def __call__(self, request, **kwargs):
            if not request.user.is_authenticated:
                raise exceptions.Unauthorized()


.. code:: python

    def login_required(view):
        def inner(request, **kwargs):
            if not request.user.is_authenticated:
                raise exceptions.Unauthorized()

        return inner
"""
import abc
from . import exceptions


class BasePermission(abc.ABC):
    def __init__(self, view_cls):
        self.view = self.view_cls = view_cls

    @abc.abstractmethod
    def __call__(self, request, **kwargs):
        return True


class LoginRequired(BasePermission):
    def __call__(self, request, **kwargs):
        if not request.user.is_authenticated:
            raise exceptions.Unauthorized()


class SuperUserRequired(BasePermission):
    def __call__(self, request, **kwargs):
        if not request.user.is_superuser:
            raise exceptions.Forbidden()


def login_required(view_cls):
    def inner(request, **kwargs):
        if not request.user.is_authenticated:
            raise exceptions.Unauthorized()

    return inner
