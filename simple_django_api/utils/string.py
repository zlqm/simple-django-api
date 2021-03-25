def ensure_str(raw, encoding='utf8'):
    if hasattr(raw, 'decode'):
        return raw.decode(encoding)
    return raw
