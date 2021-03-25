from simple_django_api.views import APIView
from .permissions import (BasicAuthRequired, login_required, owner_required)


class BasicAuthView(APIView):
    method_perms = {'GET': BasicAuthRequired}

    def get(self, request):
        return {'msg': 'hello world'}


class AuthView(APIView):
    method_perms = {'get': login_required}

    def get(self, request):
        return {'username': request.user.username}


class BlogDetailView(APIView):
    method_perms = {'get': owner_required}

    def get(self, request, pk=None):
        return {'pk': pk}
