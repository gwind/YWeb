"""
Global Yweb exception and warning classes.
"""

class YwebRuntimeWarning(RuntimeWarning):
    pass


class ImproperlyConfigured(Exception):
    """Yweb is somehow improperly configured"""
    pass


class YwebUrlError(Exception):
    pass


class YwebDBError(Exception):
    pass
