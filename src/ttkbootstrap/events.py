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

import sys
from enum import StrEnum
from typing import Union

__all__ = ["Event", "EventType", "normalize_event"]

# Public type for APIs that accept either our enum or a raw Tk sequence
EventType = Union["Event", str]

# Cross-platform accelerator key (Command on macOS, Control elsewhere)
ACCEL = "Command" if sys.platform == "darwin" else "Control"


class Event(StrEnum):
    """Canonical Tk/Tkinter event strings (keyboard, mouse, virtual, etc.)."""

    # --------------------------------------------------------------------- #
    # Mouse — buttons & wheel
    # --------------------------------------------------------------------- #

    CLICK1 = "<Button-1>"  # left press
    CLICK2 = "<Button-2>"  # middle press
    CLICK3 = "<Button-3>"  # right press

    CLICK = CLICK1  # alias

    CLICK1_DOWN = "<ButtonPress-1>"
    CLICK1_UP = "<ButtonRelease-1>"
    CLICK2_DOWN = "<ButtonPress-2>"
    CLICK2_UP = "<ButtonRelease-2>"
    CLICK3_DOWN = "<ButtonPress-3>"
    CLICK3_UP = "<ButtonRelease-3>"

    # --- Multi-click (Tk fires these on *press*) --------------------------------
    DBL_CLICK1 = "<Double-Button-1>"
    DBL_CLICK2 = "<Double-Button-2>"
    DBL_CLICK3 = "<Double-Button-3>"
    TRIPLE_CLICK1 = "<Triple-Button-1>"
    TRIPLE_CLICK2 = "<Triple-Button-2>"
    TRIPLE_CLICK3 = "<Triple-Button-3>"

    # --- Motion & Drags -------------------------------------------------- #
    MOTION = "<Motion>"
    DRAG1 = "<B1-Motion>"
    DRAG2 = "<B2-Motion>"
    DRAG3 = "<B3-Motion>"

    # Any-button helpers
    ANY_CLICK = "<Button>"  # any button press
    ANY_RELEASE = "<ButtonRelease>"  # any button release

    # Wheel (cross-platform & X11 specifics)
    MOUSE_WHEEL = "<MouseWheel>"  # use event.delta (+/-) for direction
    WHEEL_UP = "<Button-4>"  # Linux/X11
    WHEEL_DOWN = "<Button-5>"  # Linux/X11
    WHEEL_LEFT = "<Button-6>"  # optional (some X11 setups)
    WHEEL_RIGHT = "<Button-7>"  # optional (some X11 setups)

    # Hover/enter/leave
    ENTER = "<Enter>"
    LEAVE = "<Leave>"
    HOVER = ENTER  # alias

    # --------------------------------------------------------------------- #
    # Keyboard — generic & common keys
    # --------------------------------------------------------------------- #
    KEYDOWN = "<KeyPress>"
    KEYUP = "<KeyRelease>"

    RETURN = "<Return>"
    TAB = "<Tab>"
    ESCAPE = "<Escape>"

    # Activation (prefer release to mirror native behavior)
    KEYUP_RETURN = "<KeyRelease-Return>"
    KEYUP_KP_ENTER = "<KeyRelease-KP_Enter>"
    KEYUP_SPACE = "<KeyRelease-space>"
    KEYDOWN_SPACE = "<KeyPress-space>"  # handy for previews

    # Cancel / Dismiss
    KEYDOWN_ESC = "<KeyPress-Escape>"
    KEYUP_ESC = "<KeyRelease-Escape>"

    # Focus navigation
    KEYDOWN_TAB = "<KeyPress-Tab>"
    KEYUP_TAB = "<KeyRelease-Tab>"
    KEYDOWN_SHIFT_TAB = "<Shift-Tab>"  # often delivered as ISO_Left_Tab
    ISO_LEFT_TAB = "<ISO_Left_Tab>"  # X11/Linux Shift+Tab alias

    # Arrow navigation
    KEYDOWN_LEFT = "<KeyPress-Left>"
    KEYDOWN_RIGHT = "<KeyPress-Right>"
    KEYDOWN_UP = "<KeyPress-Up>"
    KEYDOWN_DOWN = "<KeyPress-Down>"
    KEYUP_LEFT = "<KeyRelease-Left>"
    KEYUP_RIGHT = "<KeyRelease-Right>"
    KEYUP_UP = "<KeyRelease-Up>"
    KEYUP_DOWN = "<KeyRelease-Down>"

    # Paging / Jump
    KEYDOWN_PAGE_UP = "<KeyPress-Prior>"  # PageUp
    KEYDOWN_PAGE_DOWN = "<KeyPress-Next>"  # PageDown
    KEYDOWN_HOME = "<KeyPress-Home>"
    KEYDOWN_END = "<KeyPress-End>"

    # Editing
    KEYDOWN_BACKSPACE = "<KeyPress-BackSpace>"
    KEYUP_BACKSPACE = "<KeyRelease-BackSpace>"
    KEYDOWN_DELETE = "<KeyPress-Delete>"
    KEYUP_DELETE = "<KeyRelease-Delete>"

    # --------------------------------------------------------------------- #
    # Modifiers / Accelerators (cross-platform helpers)
    # --------------------------------------------------------------------- #
    ACCEL_A = f"<{ACCEL}-a>"  # Select All
    ACCEL_C = f"<{ACCEL}-c>"  # Copy
    ACCEL_X = f"<{ACCEL}-x>"  # Cut
    ACCEL_V = f"<{ACCEL}-v>"  # Paste
    ACCEL_Z = f"<{ACCEL}-z>"  # Undo
    ACCEL_Y = f"<{ACCEL}-y>"  # Redo (Win/Linux)
    ACCEL_SHIFT_Z = f"<Shift-{ACCEL}-z>"  # Redo (macOS)
    ACCEL_S = f"<{ACCEL}-s>"  # Save
    ACCEL_O = f"<{ACCEL}-o>"  # Open
    ACCEL_F = f"<{ACCEL}-f>"  # Find

    # Alt / Option mnemonics (bind specific letters like Alt+F)
    ALT_ANY = "<Alt-KeyPress>"  # or use: f"<Alt-KeyPress-{letter}>"

    # --------------------------------------------------------------------- #
    # Focus / visibility / window state
    # --------------------------------------------------------------------- #
    FOCUS = "<FocusIn>"
    BLUR = "<FocusOut>"
    MOUNT = "<Map>"
    UNMOUNT = "<Unmap>"
    VISIBILITY = "<Visibility>"
    REDRAW = "<Expose>"
    DESTROY = "<Destroy>"

    # Window/configure
    CONFIGURE = "<Configure>"

    # --------------------------------------------------------------------- #
    # Virtual events (semantic / high-level)
    # --------------------------------------------------------------------- #
    INPUT = "<<Input>>"
    CHANGED = "<<Tkb-Changed>>"
    CHANGE_START = "<<Tkb-ChangeStart>>"
    CHANGE_END = "<<Tkb-ChangeEnd>>"
    MODIFIED = "<<Tkb-Modified>>"
    THEME_CHANGED = "<<ThemeChanged>>"
    INVOKE = "<<Tkb-Invoke>>"  # use to avoid clashing with built-in <<Invoke>>
    COMPLETE = "<<Tkb-Complete>>"
    WINDOW_ACTIVATED = "<<Activate>>"
    WINDOW_DEACTIVATED = "<<Deactivate>>"
    MENU_SELECT = "<<MenuSelect>>"
    SELECTION = "<<Selection>>"
    SELECTED = "<<Tkb-Selected>>"
    DESELECTED = "<<Tkb-Deselected>>"
    COMBOBOX_SELECTED = "<<ComboboxSelected>>"
    INCREMENT = "<<Increment>>"
    DECREMENT = "<<Decrement>>"
    DELETE = "<<Delete>>"
    SELECTION_CHANGED = "<<Tkb-SelectionChanged>>"

    # --------------------------------------------------------------------- #
    # Composite Widgets
    # --------------------------------------------------------------------- #

    COMPOSITE_SELECT = "<<Tkb-CompositeSelect>>"
    COMPOSITE_DESELECT = "<<Tkb-CompositeDeselect>>"

    # --------------------------------------------------------------------- #
    # Items (list, etc.)
    # --------------------------------------------------------------------- #
    ITEM_CLICK = "<<Tkb-ItemClick>>"

    ITEM_SELECTING = "<<Tkb-ItemSelecting>>"
    ITEM_SELECTED = "<<Tkb-ItemSelected>>"

    ITEM_DESELECTING = "<<Tkb-ItemDeselecting>>"
    ITEM_DESELECTED = "<<Tkb-ItemDeselected>>"

    ITEM_DELETING = "<<Tkb-ItemDeleting>>"
    ITEM_DELETED = "<<Tkb-ItemDeleted>>"
    ITEM_DELETE_FAILED = "<<Tkb-ItemDeleteFailed>>"

    ITEM_UPDATING = "<<Tkb-ItemUpdating>>"
    ITEM_UPDATED = "<<Tkb-ItemUpdated>>"
    ITEM_UPDATE_FAILED = "<<Tkb-ItemUpdateFailed>>"

    ITEM_INSERTING = "<<Tkb-ItemInserting>>"
    ITEM_INSERTED = "<<Tkb-ItemInserted>>"
    ITEM_INSERT_FAILED = "<<Tkb-ItemInsertFailed>>"

    # --------------------------------------------------------------------- #
    # Radiobutton
    # --------------------------------------------------------------------- #
    RADIO_SELECTED = SELECTED
    RADIO_DESELECTED = DESELECTED

    # --------------------------------------------------------------------- #
    # Notebook
    # --------------------------------------------------------------------- #
    NOTEBOOK_TAB_CHANGED = "<<NotebookTabChanged>>"
    NOTEBOOK_TAB_ACTIVATED = "<<NotebookTabActivated>>"
    NOTEBOOK_TAB_DEACTIVATED = "<<NotebookTabDeactivated>>"

    INPUT_METHOD_CHANGED = "<<IMChanged>>"
    TREEVIEW_SELECT = "<<TreeviewSelect>>"
    STATE_CHANGED = "<<StateChanged>>"

    TOGGLE = "<<Toggle>>"

    # --------------------------------------------------------------------- #
    # Fieldset
    # --------------------------------------------------------------------- #
    GROUP_TOGGLED = '<<GroupToggled>>'

    # --------------------------------------------------------------------- #
    # Validation
    # --------------------------------------------------------------------- #
    INVALID = "<<Invalid>>"
    VALID = "<<Valid>>"
    VALIDATED = "<<Validated>>"

    # --------------------------------------------------------------------- #
    # Navigation (app-level)
    # --------------------------------------------------------------------- #
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
