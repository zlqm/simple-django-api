from webargs.djangoparser import DjangoParser as OriginDjangoParser
from webargs.multidictproxy import MultiDictProxy


class DjangoParser(OriginDjangoParser):
    def _raw_load_json(self, req):
        return req.data


parser = DjangoParser()
use_args = parser.use_args
use_kwargs = parser.use_kwargs
