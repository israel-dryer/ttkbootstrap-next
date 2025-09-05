"""
interop.runtime.commands
------------------------

Tk/Tcl command registration helpers that wrap Python callables for use by Tkinter.

Features
- `command_wrapper`: register a plain callable as a Tcl command; supports transient (one-shot) commands.
- `trace_callback_wrapper`: register a Tcl variable trace callback, wrapping args into a `Trace`.
- `event_callback_wrapper`: register an event handler that constructs a structured `UIEvent` from raw Tcl data.

Error handling
- Exceptions raised by user callbacks are logged via the standard `logging` module
  (at ERROR level with traceback) and then re-raised.
- A pluggable `set_error_handler()` allows consumers to intercept exceptions and
  report them as they wish; if unset, logging is used.

This design avoids noisy `print()` output and integrates with application logging.
"""

from __future__ import annotations

import logging
import tkinter as tk
from functools import wraps
from typing import Any, Callable, Optional
from uuid import uuid4

from ttkbootstrap.interop.spec.types import Trace
from ttkbootstrap.interop.runtime.utils import get_event_namedtuple

__all__ = [
    "command_wrapper",
    "trace_callback_wrapper",
    "event_callback_wrapper",
    "set_error_handler",
    "get_error_handler",
]

log = logging.getLogger(__name__)

# id -> original python function (for bookkeeping; not currently used beyond cleanup)
_registered_commands: dict[str, Callable[..., Any]] = {}

# Optional pluggable error handler: (exc, context, details) -> None
# context: "command" | "trace" | "event"
# details: arbitrary context tuple (e.g., (func_name, extra_info...))
_error_handler: Optional[Callable[[BaseException, str, tuple[Any, ...]], None]] = None


def set_error_handler(handler: Optional[Callable[[BaseException, str, tuple[Any, ...]], None]]) -> None:
    """Set a custom error handler for callback exceptions."""
    global _error_handler
    _error_handler = handler


def get_error_handler() -> Optional[Callable[[BaseException, str, tuple[Any, ...]], None]]:
    """Get the current custom error handler."""
    return _error_handler


def _handle_exception(exc: BaseException, *, context: str, details: tuple[Any, ...]) -> None:
    """
    Internal: route exceptions to a custom handler if provided; otherwise log with traceback.
    Always re-raises the original exception.
    """
    if _error_handler is not None:
        try:
            _error_handler(exc, context, details)
        except Exception:  # defensive: custom handler must not break the chain
            log.exception("Error handler raised while handling %s error; falling back to logging.", context)
            log.exception("%s callback exception", context)
    else:
        log.exception("%s callback exception", context)
    # re-raise to preserve normal error semantics
    raise exc


def command_wrapper(
        widget: tk.Misc, func: Callable[..., Any], transient: bool = False, func_id: str | None = None) -> str:
    """
    Register a Tcl command for a generic Python callback.

    Args:
        widget: Tkinter widget owning the Tcl interpreter.
        func: Python callable to expose to Tcl.
        transient: If True, unregister after first successful invocation.
        func_id: Optional explicit Tcl command name.

    Returns:
        The Tcl command name registered in the interpreter.
    """
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
                    # Best effort cleanup; ignore interpreter state errors
                    pass
            return result

    widget.tk.createcommand(func_id, wrapper)
    _registered_commands[func_id] = func
    return func_id


def trace_callback_wrapper(widget: tk.Misc, func: Callable[[Trace], Any]) -> str:
    """
    Register a Tcl variable trace callback that receives a `Trace` object.

    Args:
        widget: Tkinter widget owning the Tcl interpreter.
        func: Callback accepting a `Trace(name, op)`.

    Returns:
        The Tcl command name registered in the interpreter.
    """
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
        func: Callable[[Any], Any],
        event_name: str,
        func_id: str | None = None,
        dedup: bool = False,
) -> str:
    """
    Register a Tcl command that wraps an event handler with structured payload creation.

    Args:
        widget: Tkinter widget owning the Tcl interpreter.
        func: Python event handler receiving a structured UIEvent-like payload.
        event_name: Logical event name used to build the payload (e.g., '<<Change>>').
        func_id: Optional explicit Tcl command name.
        dedup: If True, reuse a stable id for this function to avoid duplicate commands.

    Returns:
        The Tcl command name registered in the interpreter.
    """
    if dedup:
        func_id = f"evt_{id(func)}"
    elif func_id is None:
        func_id = f"evt_{uuid4().hex}"

    if func_id in _registered_commands:
        widget.tk.deletecommand(func_id)
        _registered_commands.pop(func_id, None)

    @wraps(func)
    def wrapper(*event_data):
        try:
            event_obj = get_event_namedtuple(event_name, event_data)
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
