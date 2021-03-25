=====
Usage
=====

Basic
=====

.. code:: python

   # permissions.py
   from simple_django_api.exceptions import Forbidden

   def author_required(view_cls):
       def inner(request, pk=None):
           if not request.user.is_author(pk):
               raise PermissionDenied(user_hint='only author has access to this blog')


.. code:: python

   from simple_django_api.views import APIView
   from http import HTTPStatus

   class BlogDetailView(APIView):
       method_perms = {'patch': author_required}

       def patch(self, request, pk=None):
           request.data  # you can access request body via `.data` property
           return APIResponse({}, status=HTTPStatus.NO_CONTENT)



JWT
===

.. code:: python

    # settings.py
    MIDDLEWARE = (
        ...
        'simple_django_api.jwt.middleware.AuthenticationMiddleware',
    )

    API_JWT_SECRET_KEY = 'some key'
    API_JWT_EXPIRATION_MINUTES = 0.05


.. code:: python

   # views.py
   from django.contrib.auth import authenticate
   from simple_django_api.permissions import LoginRequired
   from simple_django_api.views import APIView
   from simple_django_api.jwt.auth import generate_token


   class TokenView(APIView):
       def post(self, request):
           username = request.data['username']
           password = request.data['password']
           user = authenticate(request, username=username, password=password)
           if user is not None:
               token = generate_token(user)
               return APIResponse.created({'token': token})
           body = {'detail': 'invalid username or password'}
           return APIResponse(body, status_code=HTTPStatus.BAD_REQUEST)


   class ProfileView(APIView):
       method_perms = {'GET': LoginRequired}

       def get(self, request):
           return {'username': request.user.username}
