=================
simple-django-api
=================


.. image:: https://img.shields.io/pypi/v/simple_django_api.svg
        :target: https://pypi.python.org/pypi/simple_django_api

.. image:: https://img.shields.io/travis/zlqm/simple_django_api.svg
        :target: https://travis-ci.com/zlqm/simple_django_api

.. image:: https://readthedocs.org/projects/simple-django-api/badge/?version=latest
        :target: https://simple-django-api.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


Simple library provides rest api for Django.

* Free software: BSD license
* Documentation: https://simple-django-api.readthedocs.io.


This project is mainly to solve problems below:

  * Django doesn't support PUT/PATCH request with request body.
  * Django doesn't support request body in JSON format.


Features
--------

1. Support request body in json format
2. Support PUT/PATCH method with request body
3. Class-Based-View exception handler
4. Dynamic permission check
5. JWT(Json Web Token) auth middleware


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
