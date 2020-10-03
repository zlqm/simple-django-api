########################
django_improved_view
########################

1. parse request body when request method is PUT, PATCH.
2. support json request body.
3. add expcetion handle for CBV(Class Based View)
4. add permission check for CBV



***********
Install
***********

.. code:: bash

   $: pip install django_improved_view


*********
Usuage
*********

.. code:: python

    from django_improved_view import exceptions, permissions
    from django_improved_view.response import APIResponse
    from django_improved_view.views import APIView
    from django_improved_view.permissions import BasePermission


    class BasicAuthRequiredError(exceptions.APIException):
        HTTP_STATUS_CODE = 401
        ERROR_CODE = 10000


    class TokenRequired(BasePermission):
        def __call__(self):
            if not self.request.headers.get('Authorization'):
                raise BasicAuthRequiredError(user_hint='basic auth required')


    class PermissionView(APIView):
        method_perms = {'POST': [TokenRequired]}

        def post(self, request):
            return APIResponse.ok({})



*************
Test
*************


.. code:: python

   $: pytest tests
