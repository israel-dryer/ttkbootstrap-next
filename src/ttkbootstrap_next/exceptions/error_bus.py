import logging
from typing import Callable, List

log = logging.getLogger(__name__)
ErrorHandler = Callable[[BaseException], None]


class ErrorBus:
    _subs: List[ErrorHandler] = []

    @classmethod
    def subscribe(cls, fn: ErrorHandler):
        cls._subs.append(fn)

    @classmethod
    def emit(cls, err: BaseException):
        for fn in list(cls._subs):
            try:
                fn(err)
            except Exception:
                log.exception("error handler failed")
