"""
interop.runtime.commands
------------------------

Register Python callables as Tcl/Tk commands.

- command_wrapper: plain Tcl command (optionally one-shot).
- trace_callback_wrapper: var-trace command (wraps args into a lightweight Trace).
- event_callback_wrapper: event handler; builds a minimal, per-event payload
  using `runtime.event_factory.builder_for(...)` and passes it to the callback.

Errors are routed to an optional custom handler and otherwise logged, then re-raised.
"""

from __future__ import annotations

import logging
from collections import namedtuple
from functools import wraps
from typing import Any, Callable, Optional
from uuid import uuid4

import tkinter as tk  # keep tkinter import isolated for runtime layer

from ttkbootstrap_next.interop.runtime.event_factory import builder_for
from ttkbootstrap_next.interop.runtime.event_types import BaseEvent

__all__ = [
    "command_wrapper",
    "trace_callback_wrapper",
    "event_callback_wrapper",
    "set_error_handler",
    "get_error_handler",
]

log = logging.getLogger(__name__)

# Lightweight container for Tcl variable trace notifications.
Trace = namedtuple("Trace", "name operation")

# Bookkeeping: Tcl command id -> original Python function
_registered_commands: dict[str, Callable[..., Any]] = {}

# Optional pluggable error handler: (exc, context, details) -> None
_error_handler: Optional[Callable[[BaseException, str, tuple[Any, ...]], None]] = None


def set_error_handler(handler: Optional[Callable[[BaseException, str, tuple[Any, ...]], None]]) -> None:
    """Set a custom error handler for callback exceptions."""
    global _error_handler
    _error_handler = handler


def get_error_handler() -> Optional[Callable[[BaseException, str, tuple[Any, ...]], None]]:
    """Return the current custom error handler, if any."""
    return _error_handler


def _handle_exception(exc: BaseException, *, context: str, details: tuple[Any, ...]) -> None:
    """Dispatch exceptions to a custom handler if provided; else log and re-raise."""
    handler = _error_handler
    if handler is not None:
        try:
            handler(exc, context, details)
        except Exception:
            log.exception("Error handler raised while handling %s error; falling back to logging.", context)
            log.exception("%s callback exception", context, exc_info=exc)
    else:
        log.exception("%s callback exception", context, exc_info=exc)
    raise exc


def command_wrapper(
        widget: tk.Misc,
        func: Callable[..., Any],
        transient: bool = False,
        func_id: str | None = None,
) -> str:
    """Register a plain Tcl command for a Python callable (optionally one-shot)."""
    if func_id is None:
        func_id = f"cmd_{uuid4().hex}"

    if func_id in _registered_commands:
        widget.tk.deletecommand(func_id)
        _registered_commands.pop(func_id, None)

    @wraps(func)
    def wrapper(*args):
        try:
            result = func(*args)
        except BaseException as exc:
            _handle_exception(exc, context="command", details=(func.__name__, args))
        else:
            if transient:
                try:
                    widget.tk.deletecommand(func_id)
                    _registered_commands.pop(func_id, None)
                except Exception:
                    # Best-effort cleanup; ignore interpreter state errors
                    pass
            return result

    widget.tk.createcommand(func_id, wrapper)
    _registered_commands[func_id] = func
    return func_id


def trace_callback_wrapper(widget: tk.Misc, func: Callable[[Trace], Any]) -> str:
    """Register a Tcl var-trace command that passes a `Trace(name, operation)`."""
    func_id = f"trace_{uuid4().hex}"

    @wraps(func)
    def wrapper(name, index, op):
        try:
            return func(Trace(name, op))
        except BaseException as exc:
            _handle_exception(exc, context="trace", details=(func.__name__, name, index, op))

    widget.tk.createcommand(func_id, wrapper)
    _registered_commands[func_id] = func
    return func_id


def event_callback_wrapper(
        widget: tk.Misc,
        func: Callable[[BaseEvent], Any],
        event_name: str,
        func_id: str | None = None,
        dedup: bool = False,
) -> str:
    """
    Register a Tcl event command.

    Builds the minimal, pattern-specific event payload using a cached builder
    (`runtime.event_factory.builder_for(event_name)`) and passes it to the
    Python callback.
    """
    if dedup:
        func_id = f"evt_{id(func)}"
    elif func_id is None:
        func_id = f"evt_{uuid4().hex}"

    if func_id in _registered_commands:
        widget.tk.deletecommand(func_id)
        _registered_commands.pop(func_id, None)

    # Resolve and cache the builder once per registration (micro-opt).
    build = builder_for(event_name)

    @wraps(func)
    def wrapper(*event_data):
        try:
            event_obj = build(event_name, event_data)  # -> specific slots dataclass
            return func(event_obj)
        except BaseException as exc:
            _handle_exception(
                exc,
                context="event",
                details=(func.__name__, event_name, event_data),
            )

    widget.tk.createcommand(func_id, wrapper)
    _registered_commands[func_id] = func
    return func_id
