"""
interop.runtime.substitutions
-----------------------------

Runtime helpers for managing event substitution definitions.

Tkinter events can substitute raw values (e.g. `%x`, `%y`, `%K`) into
event callback strings. The `interop.spec.constants.event_subs` list
defines which substitutions are supported and how to convert them into
typed values.

This module provides:
- `register_event_sub`: extend the substitution list at runtime by adding
  new `Sub(name, code, converter)` entries.
- `get_event_substring`: return a cached Tcl substitution string built
  from the codes in `event_subs`. This string is passed to Tcl when
  binding events so the correct values are interpolated.

Example:

    from ttkbootstrap_next.interop.runtime.substitutions import register_event_sub

    # add a new substitution for a hypothetical %Z code
    register_event_sub("zoom", "%Z", int)
"""

from typing import Callable

from ttkbootstrap_next.interop.spec.subs import Sub, event_subs
from ttkbootstrap_next.interop.runtime.utils import get_substring


def register_event_sub(name: str, code: str, converter: Callable):
    """Append a new event substitution to the global list."""
    event_subs.append(Sub(name, code, converter))


def get_event_substring() -> str:
    """Return the cached space-delimited substitution string for Tcl bindings."""
    global _event_sub_string
    if _event_sub_string is None:
        _event_sub_string = get_substring(event_subs)
    return _event_sub_string


_event_sub_string: str | None = None
