import django
from django.conf import settings
from django.core import management

from .demo_app import settings as project_settings


def setup_django():
    settings.configure(
        **{
            key: getattr(project_settings, key)
            for key in dir(project_settings) if key.isupper()
        })
    django.setup()


collect_ignore = []
if django.__version__[:3] > '2.2':
    collect_ignore.append('request/django_2x/')
else:
    collect_ignore.append('request/django_3x/')

setup_django()
management.call_command('makemigrations')
management.call_command('migrate')
