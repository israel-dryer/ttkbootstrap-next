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
- ``convert_event_widget``: resolve Tk pathname or a custom id to the
  ttkbootstrap widget via the registry; falls back to the original str.

Integration
-----------
These converters are referenced in the substitution specifications
defined in :mod:`interop.spec.constants` (``event_subs`` and
``validation_subs``). Each `Sub` entry uses one of these functions to
convert raw Tcl values into Python types before being attached to an
event payload.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from json import JSONDecodeError

from typing import Any


def convert_event_timestamp(seconds: str) -> str:
    """Convert seconds to an ISO-8601 UTC timestamp string."""
    return datetime.fromtimestamp(int(seconds), tz=timezone.utc).isoformat().replace("+00:00", "Z")


def convert_event_state(state: str | int) -> int | str:
    """Convert state to int if possible; otherwise return as-is."""
    try:
        return int(state)
    except (TypeError, ValueError):
        return state


def convert_event_data(data: str):
    """Best-effort JSON decode with Tcl backslash-escape cleanup."""
    # try plain JSON first
    try:
        return json.loads(data)
    except (TypeError, JSONDecodeError):
        pass
    # strip Tcl backslash-escapes for { } " \ and space, then parse
    if isinstance(data, str):
        cleaned = re.sub(r'\\([{}"\\ ])', r'\1', data)
        try:
            return json.loads(cleaned)
        except JSONDecodeError:
            return {}
    return {}


def convert_event_widget(name: str) -> Any:
    """
    Resolve a widget name to the ttkbootstrap wrapper when possible.

    - If `name` looks like a Tk pathname (starts with '.'), we look it up by Tk path.
    - Otherwise we try a custom id lookup first, then fall back to a Tk path lookup.
    - If not found (widget destroyed or not registered yet), return the original string.

    Returns
    -------
    Any
        The ttkbootstrap widget wrapper when found; otherwise the original `name` string.
        (Typed as `Any` by design for convenience in event payload code.)
    """
    if not name:
        return name  # keep it simple; validators can handle empty/None if needed

    # Lazy import to avoid import cycles and keep this module lightweight.
    try:
        from ttkbootstrap.core.widget_registry import by_tk, by_id
    except Exception:
        # Registry not available during early import stages → return the raw name.
        return name

    # Heuristic: Tk path_names always start with "."
    widget = by_tk(name) if name[0] == "." else (by_id(name) or by_tk(name))
    return widget if widget is not None else name
