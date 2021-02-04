from django.conf import settings


class SettingsProxy:
    def __init__(self, **default):
        self._default = {key.upper(): value for key, value in default.items()}

    def __getattr__(self, name):
        if name in self._default:
            if hasattr(settings, name):
                return getattr(settings, name)
            return self._default[name]
        return getattr(settings, name)
