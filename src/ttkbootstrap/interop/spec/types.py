"""
interop.spec.types
------------------

Type definitions for event interop.

This module defines the static data structures used to represent event
substitutions and structured event payloads. These types are referenced
by `interop.spec.constants` (for substitution specs) and consumed by
`interop.runtime` (for event mapping, command wrappers, etc.).

Contents
--------
- ``Sub``: namedtuple describing a substitution (name, code, converter).
- ``Trace``: namedtuple representing a Tcl variable trace notification.
- Dataclasses (all inherit from PrunableEventMixin for `to_payload`):
    - ``EventInput``: input-related fields (keysym, state, modifiers, etc.).
    - ``EventGeometry``: widget geometry and pointer coordinates.
    - ``EventWindowing``: window/subwindow/focus details.
    - ``EventMeta``: miscellaneous metadata (mode, place, property).
    - ``EventValidation``: entry/spinbox validation callback fields.
    - ``EventRef``: references to widget and root identifiers.
    - ``UIEvent``: top-level event container tying all substructures.

Usage
-----
The runtime layer constructs these dataclasses from raw event data,
then prunes them into NamedNamespaces or dicts using the mixin. This
ensures structured, typed payloads are delivered to user callbacks.

Example::

    ui_event = UIEvent(
        name="<<Change>>",
        input=EventInput(keysym="a", char="a", state="8", mods=("Alt",), press="A", delta=0.0)
    )
    print(ui_event.to_payload())
    # UIEvent(name='<<Change>>', input=EventInput(keysym='a', ...))
"""

from collections import namedtuple
from dataclasses import dataclass
from typing import Optional

from ttkbootstrap.interop.foundation.prune import PrunableEventMixin

# Basic substitution / trace descriptors
Sub = namedtuple("Sub", "name code converter")
Trace = namedtuple("Trace", "name operation")


@dataclass(slots=True)
class EventInput(PrunableEventMixin):
    """Input-related event fields: key symbol, char, state, modifiers, press, delta."""
    keysym: Optional[str]
    char: Optional[str]
    state: Optional[str]
    mods: tuple[str, ...]
    press: Optional[str]
    delta: float


@dataclass(slots=True)
class EventGeometry(PrunableEventMixin):
    """Geometry-related fields: widget size and pointer coordinates."""
    x: int
    y: int
    x_root: int
    y_root: int
    width: int
    height: int
    border_width: int


@dataclass(slots=True)
class EventWindowing(PrunableEventMixin):
    """Windowing-related fields: window IDs, subwindows, focus, etc."""
    window: int
    subwindow: int
    send_event: int
    override_redirect: str
    focus: int


@dataclass(slots=True)
class EventMeta(PrunableEventMixin):
    """Metadata fields such as mode, place, and property."""
    mode: str
    place: str
    property: str


@dataclass(slots=True)
class EventValidation(PrunableEventMixin):
    """Validation callback fields for entry/spinbox widgets."""
    action_type: int
    char_index: int
    validation_value: str
    current_value: str
    insert_value: str
    condition: str


@dataclass(slots=True)
class EventRef(PrunableEventMixin):
    """References to the widget and root identifiers."""
    root: str
    widget: str


@dataclass(slots=True)
class UIEvent(PrunableEventMixin):
    """Top-level structured event object tying all substructures together."""
    name: str
    timestamp: str | None = None
    data: dict | None = None
    input: EventInput | None = None
    geometry: EventGeometry | None = None
    ref: EventRef | None = None
    meta: EventMeta | None = None
    windowing: EventWindowing | None = None
    validation: EventValidation | None = None
