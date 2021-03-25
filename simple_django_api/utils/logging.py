from collections import OrderedDict


class LoggingContext(OrderedDict):
    def __init__(self, delimiter=' '):
        self.delimiter = delimiter

    def __str__(self):
        parts = [f'[{key}: {value}]' for key, value in self.items()]
        return self.delimiter.join(parts)
