import tkinter as tk
from functools import wraps
from typing import Any, Callable
from uuid import uuid4

from ttkbootstrap.interop.types import Trace
from ttkbootstrap.interop.utils import get_event_namedtuple

_registered_commands: dict[str, Callable] = {}


def command_wrapper(widget: tk.Misc, func: Callable, transient=False, func_id: str = None) -> str:
    """Register a Tcl command for a generic callback."""
    if func_id is None:
        func_id = f'cmd_{uuid4().hex}'

    if func_id in _registered_commands:
        widget.tk.deletecommand(func_id)
        _registered_commands.pop(func_id, None)

    @wraps(func)
    def wrapper(*args):
        try:
            result = func(*args)
        except Exception:
            import traceback
            print(f"\n🔴 Exception in command callback: {func.__name__}")
            traceback.print_exc()
            raise
        else:
            if transient:
                try:
                    widget.tk.deletecommand(func_id)
                    _registered_commands.pop(func_id, None)
                except Exception:
                    pass
            return result

    widget.tk.createcommand(func_id, wrapper)
    _registered_commands[func_id] = func
    return func_id


def trace_callback_wrapper(widget: tk.Misc, func: Callable[[Trace], Any]) -> str:
    """Register a Tcl trace variable callback."""
    func_id = f'trace_{uuid4().hex}'

    @wraps(func)
    def wrapper(name, index, op):
        return func(Trace(name, op))

    widget.tk.createcommand(func_id, wrapper)
    _registered_commands[func_id] = func
    return func_id


def event_callback_wrapper(
        widget: tk.Misc,
        func: Callable[[Any], Any],
        event_name: str,
        func_id: str = None,
        dedup: bool = False
) -> str:
    """Register a Tcl command that wraps an event callback with event object construction."""
    if dedup:
        func_id = f'evt_{id(func)}'
    elif func_id is None:
        func_id = f'evt_{uuid4().hex}'

    if func_id in _registered_commands:
        widget.tk.deletecommand(func_id)
        _registered_commands.pop(func_id, None)

    @wraps(func)
    def wrapper(*event_data):
        try:
            event_obj = get_event_namedtuple(event_name, event_data)
            return func(event_obj)
        except Exception:
            import traceback
            print(f"\n❌ Exception in event handler: {func.__name__} for <<{event_name}>>")
            print("Event data:", event_data)
            traceback.print_exc()
            raise

    widget.tk.createcommand(func_id, wrapper)
    _registered_commands[func_id] = func
    return func_id
