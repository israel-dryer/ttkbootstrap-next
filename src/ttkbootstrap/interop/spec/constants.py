"""
interop.spec.constants
----------------------

Static substitution specifications for Tkinter events.

Tkinter passes event information into callbacks using substitution codes
(e.g. ``%x`` for mouse x-coordinate, ``%K`` for key symbol). These codes
must be expanded in the Tcl binding string and then converted into
Python-friendly types.

This module defines two global lists of `Sub` objects:

- ``event_subs`` — the standard substitutions for general Tk events
  (keyboard, mouse, geometry, windowing, metadata, widget references,
  and custom data). Each entry specifies:
    - a field name (e.g. ``"keysym"``),
    - a Tcl substitution code (e.g. ``"%K"``),
    - a converter function to transform the raw string.

- ``validation_subs`` — substitutions specific to Tk validation callbacks
  on entry/spinbox widgets (e.g. ``"%P"`` for proposed value).

These lists are consumed by runtime helpers such as
``interop.runtime.utils.map_event_data`` and
``interop.runtime.substitutions.get_event_substring`` to build structured
event payloads.

Example
-------
    from ttkbootstrap.interop.spec.constants import event_subs

    for sub in event_subs:
        print(sub.name, sub.code)

    # -> 'type' %T
    # -> 'keysym' %K
    # ...
"""

from ttkbootstrap.interop.spec.converters import (
    convert_event_data, convert_event_state, convert_event_timestamp,
    convert_event_type, convert_event_widget,
)
from ttkbootstrap.interop.spec.types import Sub

# Standard Tk event substitutions
event_subs: list[Sub] = [
    # Input
    Sub("type", "%T", convert_event_type),
    Sub("keysym", "%K", str),
    Sub("char", "%A", str),
    Sub("state", "%s", convert_event_state),
    Sub("delta", "%D", float),

    # Position
    Sub("x", "%x", int),
    Sub("y", "%y", int),
    Sub("x_root", "%X", int),
    Sub("y_root", "%Y", int),

    # Geometry
    Sub("width", "%w", int),
    Sub("height", "%h", int),
    Sub("border_width", "%B", int),

    # Windowing
    Sub("window", "%i", hex),
    Sub("subwindow", "%S", hex),
    Sub("send_event", "%E", hex),
    Sub("override_redirect", "%o", str),
    Sub("focus", "%f", int),

    # Metadata
    Sub("timestamp", "[clock seconds]", convert_event_timestamp),
    Sub("mode", "%m", str),
    Sub("place", "%p", str),
    Sub("property", "%P", str),

    # Widget references
    Sub("root", "%R", convert_event_widget),
    Sub("widget", "%W", convert_event_widget),

    # Custom
    Sub("data", "%d", convert_event_data),
]

# Validation-specific substitutions for Entry/Spinbox
validation_subs: list[Sub] = [
    Sub("action_type", "%d", int),
    Sub("char_index", "%i", int),
    Sub("validation_value", "%P", str),
    Sub("current_value", "%s", str),
    Sub("insert_value", "%S", str),
    Sub("state", "%v", str),
    Sub("condition", "%V", str),
    Sub("widget", "%W", convert_event_widget),
]
