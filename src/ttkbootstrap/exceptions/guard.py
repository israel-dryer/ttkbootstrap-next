import logging
from functools import wraps
from ttkbootstrap.exceptions.base import UIError, wrap_with_cause
from ttkbootstrap.exceptions.error_bus import ErrorBus

log = logging.getLogger(__name__)


def guard(fn):
    @wraps(fn)
    def wrapped(*a, **kw):
        try:
            return fn(*a, **kw)
        except UIError as e:
            log.exception("UI error")
            ErrorBus.emit(e)  # already user-facing
        except Exception as e:
            log.exception("Unexpected error")  # full traceback for devs
            ErrorBus.emit(wrap_with_cause("Unexpected internal error", e))

    return wrapped
