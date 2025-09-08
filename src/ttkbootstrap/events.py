"""
ttkbootstrap.events
-------------------

Canonical Tk/Tkinter event strings and lightweight typing.

Exports
-------
- `Event` (StrEnum): canonical Tk/Tkinter event strings (e.g., "<Return>", "<<Change>>").
- `EventType`: Union[Event, str] for user-facing APIs that accept either.
- `normalize_event(ev) -> str`: helper to convert EventType to a Tk event sequence.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Union

__all__ = ["Event", "EventType", "normalize_event"]

EventType = Union["Event", str]


class Event(StrEnum):
    """Canonical Tk/Tkinter event strings (keyboard, mouse, virtual, etc.)."""

    # Mouse (buttons)
    CLICK = "<Button-1>"
    RIGHT_CLICK = "<Button-3>"
    MIDDLE_CLICK = "<Button-2>"
    DBL_CLICK = "<Double-Button-1>"
    MOUSE_DOWN = "<ButtonPress>"
    MOUSE_UP = "<ButtonRelease>"

    # Mouse (wheel)
    MOUSE_WHEEL = "<MouseWheel>"
    WHEEL_UP = "<Button-4>"  # Linux/X11
    WHEEL_DOWN = "<Button-5>"  # Linux/X11

    # Pointer motion/drag
    DRAG = "<B1-Motion>"
    MOTION = "<Motion>"

    # Enter/leave (HOVER is an alias of ENTER)
    ENTER = "<Enter>"
    HOVER = "<Enter>"
    LEAVE = "<Leave>"

    # Keyboard (generic)
    KEYDOWN = "<KeyPress>"
    KEYUP = "<KeyRelease>"

    # Keyboard (common keys)
    RETURN = "<Return>"
    TAB = "<Tab>"
    ESCAPE = "<Escape>"

    # Keyboard (specific key transitions)
    KEYDOWN_ENTER = "<KeyPress-Return>"
    KEYUP_ENTER = "<KeyRelease-Return>"
    KEYDOWN_ESC = "<KeyPress-Escape>"
    KEYUP_ESC = "<KeyRelease-Escape>"
    KEYDOWN_TAB = "<KeyPress-Tab>"
    KEYUP_TAB = "<KeyRelease-Tab>"

    # Focus / visibility / map state
    FOCUS = "<FocusIn>"
    BLUR = "<FocusOut>"
    MOUNT = "<Map>"
    UNMOUNT = "<Unmap>"
    VISIBILITY = "<Visibility>"
    REDRAW = "<Expose>"
    DESTROY = "<Destroy>"

    # Window/configure
    CONFIGURE = "<Configure>"

    # Virtual events
    INPUT = "<<Input>>"
    CHANGED = "<<Changed>>"
    MODIFIED = "<<Modified>>"
    THEME_CHANGED = "<<ThemeChanged>>"

    COMPLETE = "<<Complete>>"
    WINDOW_ACTIVATED = "<<Activate>>"
    WINDOW_DEACTIVATED = "<<Deactivate>>"
    MENU_SELECT = "<<MenuSelect>>"
    SELECTION = "<<Selection>>"
    SELECTED = "<<Selected>>"
    DESELECTED = "<<Deselected>>"
    COMBOBOX_SELECTED = "<<ComboboxSelected>>"
    INCREMENT = "<<Increment>>"
    DECREMENT = "<<Decrement>>"
    DELETE = "<<Delete>>"
    NOTEBOOK_TAB_CHANGED = "<<NotebookTabChanged>>"
    INPUT_METHOD_CHANGED = "<<IMChanged>>"
    TREEVIEW_SELECT = "<<TreeviewSelect>>"
    STATE_CHANGED = "<<StateChanged>>"

    # Validation
    INVALID = "<<Invalid>>"
    VALID = "<<Valid>>"
    VALIDATED = "<<Validated>>"

    # Navigation
    PAGE_WILL_MOUNT = "<<PageWillMount>>"
    PAGE_MOUNTED = "<<PageMounted>>"
    PAGE_UNMOUNTED = "<<PageUnmounted>>"
    PAGE_CHANGED = "<<PageChanged>>"


def normalize_event(ev: EventType) -> str:
    """
    Normalize an Event or str to a Tk event sequence string.

    Parameters
    ----------
    ev : EventType
        Either an Event enum member or a raw Tk sequence string.

    Returns
    -------
    str
        The Tk event sequence (e.g., "<Return>", "<<Changed>>").

    Raises
    ------
    TypeError
        If `ev` is neither an Event nor a str.
    """
    if isinstance(ev, Event):
        return str(ev)
    if isinstance(ev, str):
        return ev
    raise TypeError(f"Unsupported event: {ev!r}")
