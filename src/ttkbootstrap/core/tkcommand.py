import json
from json import JSONDecodeError
from datetime import datetime
from functools import wraps
from collections import namedtuple
from typing import Callable, Any, Sequence
from uuid import uuid4
import tkinter as tk
import enum


# ---------------------------------------------------------------------
# EventEnum Definition
# ---------------------------------------------------------------------

class EventEnum(enum.IntEnum):
    KeyPress = 2
    KeyRelease = 3
    ButtonPress = 4
    ButtonRelease = 5
    Motion = 6
    Enter = 7
    Leave = 8
    FocusIn = 9
    FocusOut = 10
    Keymap = 11
    Expose = 12
    GraphicsExpose = 13
    NoExpose = 14
    Visibility = 15
    Create = 16
    Destroy = 17
    Unmap = 18
    Map = 19
    MapRequest = 20
    Reparent = 21
    Configure = 22
    ConfigureRequest = 23
    Gravity = 24
    ResizeRequest = 25
    Circulate = 26
    CirculateRequest = 27
    Property = 28
    SelectionClear = 29
    SelectionRequest = 30
    Selection = 31
    Colormap = 32
    ClientMessage = 33
    Mapping = 34
    VirtualEvent = 35
    Activate = 36
    Deactivate = 37
    MouseWheel = 38

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, EventEnum):
            return self.value == other.value
        if isinstance(other, str):
            return self.name == other
        return NotImplemented


# ---------------------------------------------------------------------
# Conversion Functions
# ---------------------------------------------------------------------

def convert_event_timestamp(seconds):
    return datetime.fromtimestamp(int(seconds))


def convert_event_state(state):
    try:
        return int(state)
    except (TypeError, ValueError):
        return state


def convert_event_data(data):
    try:
        return json.loads(data)
    except JSONDecodeError:
        return data


def convert_event_type(type_code):
    return EventEnum(int(type_code))


def convert_event_widget(name):
    return name  # Can be extended to resolve widget references


# ---------------------------------------------------------------------
# Substitution Descriptors
# ---------------------------------------------------------------------

Sub = namedtuple('Sub', 'name code converter')
Trace = namedtuple('Trace', 'name operation')

event_subs: list[Sub] = [
    # Input
    Sub('type', '%T', convert_event_type),
    Sub('keysym', '%K', str),
    Sub('char', '%A', str),
    Sub('state', '%s', convert_event_state),
    Sub('delta', '%D', float),

    # Position
    Sub('x', '%x', int),
    Sub('y', '%y', int),
    Sub('x_root', '%X', int),
    Sub('y_root', '%Y', int),

    # Geometry
    Sub('width', '%w', int),
    Sub('height', '%h', int),
    Sub('border_width', '%B', int),

    # Windowing
    Sub('window', '%i', hex),
    Sub('subwindow', '%S', hex),
    Sub('send_event', '%E', hex),
    Sub('override_redirect', '%o', str),
    Sub('focus', '%f', int),

    # Metadata
    Sub('time', '[clock seconds]', convert_event_timestamp),
    Sub('mode', '%m', str),
    Sub('place', '%p', str),
    Sub('property', '%P', str),

    # Widget references
    Sub('root', '%R', convert_event_widget),
    Sub('widget', '%W', convert_event_widget),

    # Custom
    Sub('data', '%d', convert_event_data),
]

validation_subs: list[Sub] = [
    Sub('action_type', '%d', int),
    Sub('char_index', '%i', int),
    Sub('validation_value', '%P', str),
    Sub('current_value', '%s', str),
    Sub('insert_value', '%S', str),
    Sub('state', '%v', str),
    Sub('condition', '%V', str),
    Sub('widget', '%W', convert_event_widget)
]


def register_event_sub(name: str, code: str, converter: Callable):
    """Allow runtime extension of event substitutions."""
    event_subs.append(Sub(name, code, converter))


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

_namedtuple_cache = {}


def dict_to_namedtuple(name: str, dictionary: dict[str, Any]):
    """Convert a dictionary to a namedtuple, caching the structure."""
    key = tuple(dictionary.keys())
    if key not in _namedtuple_cache:
        _namedtuple_cache[key] = namedtuple(name, key)
    return _namedtuple_cache[key](**dictionary)


def get_substring(sublist: list[Sub]) -> str:
    return ' '.join([e.code for e in sublist])


_event_sub_string = None


def get_event_substring() -> str:
    global _event_sub_string
    if _event_sub_string is None:
        _event_sub_string = get_substring(event_subs)
    return _event_sub_string


def map_event_data(event_data: Sequence[str], subs: list[Sub]) -> dict[str, Any]:
    out_data = {}
    for i, sub in enumerate(event_data):
        if sub != '??':
            try:
                key = subs[i].name
                val = subs[i].converter(sub)
                if val is not None:
                    out_data[key] = val
            except (TypeError, IndexError):
                continue
    return out_data


def get_event_namedtuple(event_name: str, raw_data: Sequence[str]) -> Any:
    """Create a namedtuple event object from raw event data."""
    event_dict = {'name': event_name}
    event_dict.update(map_event_data(raw_data, event_subs))
    return dict_to_namedtuple('Event', event_dict)


# ---------------------------------------------------------------------
# Command + Event Callback Registration
# ---------------------------------------------------------------------

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
