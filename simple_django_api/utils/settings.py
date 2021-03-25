from django.conf import settings


class FallbackSettings:
    def __init__(self, **default):
        self._default = {key.upper(): value for key, value in default.items()}

    def __getattr__(self, name):
        try:
            return getattr(settings, name)
        except AttributeError as exc:
            if name in self._default:
                return self._default[name]
            raise AttributeError from exc
