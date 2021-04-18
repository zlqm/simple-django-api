"""Utilities for random stuff
"""
import string
import secrets


def get_random_string(length=12,
                      allowed_chars=string.ascii_letters + string.digits):
    """Return a securely generated random string.
    """
    return ''.join(secrets.choice(allowed_chars) for _ in range(length))
