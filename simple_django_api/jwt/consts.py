import enum


class TokenCase(enum.Enum):
    OK = enum.auto()
    NO_TOKEN = enum.auto()
    EXPIRED = enum.auto()
    DECODE_ERROR = enum.auto()
    INVALID_TOKEN = enum.auto()
    MISSING_KEY = enum.auto()
