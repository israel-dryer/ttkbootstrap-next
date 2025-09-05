"""
interop.spec.converters
-----------------------

Converter functions for transforming raw Tcl event substitution values
into Python-friendly objects.

Tkinter passes all substitution values as strings. These helpers convert
them into the appropriate types before they are attached to structured
event payloads.

Converters
----------
- ``convert_event_timestamp``: seconds → UTC ISO-8601 string (Z suffix).
- ``convert_event_state``: string → int (if possible), else raw value.
- ``convert_event_data``: JSON string → dict/list, else raw value.
- ``convert_event_type``: int code → ``EventEnum``.
- ``convert_event_widget``: returns the widget name (placeholder for
  future resolution to actual widget objects).

Integration
-----------
These converters are referenced in the substitution specifications
defined in :mod:`interop.spec.constants` (``event_subs`` and
``validation_subs``). Each `Sub` entry uses one of these functions to
convert raw Tcl values into Python types before being attached to an
event payload.
"""

import json
from datetime import datetime, timezone
from json import JSONDecodeError

from ttkbootstrap.interop.foundation.events import EventEnum


def convert_event_timestamp(seconds: str) -> str:
    """Convert seconds to an ISO-8601 UTC timestamp string."""
    return datetime.fromtimestamp(int(seconds), tz=timezone.utc).isoformat().replace("+00:00", "Z")


def convert_event_state(state: str | int) -> int | str:
    """Convert state to int if possible; otherwise return as-is."""
    try:
        return int(state)
    except (TypeError, ValueError):
        return state


def convert_event_data(data: str) -> object:
    """Parse JSON string to Python object; return raw data on failure."""
    try:
        return json.loads(data)
    except JSONDecodeError:
        return data


def convert_event_type(type_code: str | int) -> EventEnum:
    """Convert event type code to an EventEnum."""
    return EventEnum(int(type_code))


def convert_event_widget(name: str) -> str:
    """Return widget name; placeholder for widget reference resolution."""
    return name
