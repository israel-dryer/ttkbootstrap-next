from enum import StrEnum
from typing import Union


class Event(StrEnum):
    # mouse events
    CLICK = "<Button-1>"
    RIGHT_CLICK = "<Button-3>"
    MIDDLE_CLICK = "<Button-2>"
    DBL_CLICK = "<Double-Button-1>"
    DRAG = "<B1-Motion>"
    MOUSE_WHEEL = "<MouseWheel>"
    WHEEL_UP = "<Button-4>"  # linux
    WHEEL_DOWN = "<Button-5>"  # linux
    HOVER = "<Enter>"
    ENTER = "<Enter>"
    LEAVE = "<Leave>"
    MOUSE_DOWN = "<ButtonPress>"
    MOUSE_UP = "<ButtonRelease>"

    # keyboard events
    KEYDOWN = "<KeyPress>"
    KEYUP = "<KeyRelease>"
    KEYDOWN_ENTER = "<KeyPress-Return>"
    KEYUP_ENTER = "<KeyRelease-Return>"
    KEYDOWN_ESC = "<KeyRelease-Escape>"
    KEYUP_ESC = "<KeyRelease-Escape>"
    KEYDOWN_TAB = "<KeyPress-Tab>"
    KEYUP_TAB = "<KeyRelease-Tab>"

    # Focus and Visibility
    FOCUS = "<FocusIn>"
    BLUR = "<FocusOut>"
    MOUNT = "<Map>"
    UNMOUNT = "<Unmap>"
    VISIBILITY = "<Visibility>"
    REDRAW = "<Expose>"
    DESTROY = "<Destroy>"

    # General Input aliases
    RETURN = "<Return>"
    TAB = "<Tab>"
    ESCAPE = "<Escape>"

    # Motion and resize
    MOTION = "<Motion>"
    CONFIGURE = "<Configure>"

    # Virtual Events (<<...>>)
    CHANGED = "<<Changed>>"
    MODIFIED = "<<Modified>>"
    THEME_CHANGED = "<<ThemeChanged>>"

    MENU_SELECTED = "<<MenuSelected>>"
    SELECTION = "<<Selection>>"
    SELECTED = "<<Selected>>"
    DESELECTED = "<<Deselected>>"
    COMBOBOX_SELECTED = "<<ComboboxSelected>>"
    INCREMENT = "<<Increment>>"
    DECREMENT = "<<Decrement>>"
    NOTEBOOK_TAB_CHANGED = "<<NotebookTabChanged>>"
    NOTEBOOK_TAB_ACTIVATE = "<<Activate>>"
    NOTEBOOK_TAB_DEACTIVATE = "<<Deactivate>>"
    INPUT_METHOD_CHANGED = '<<IMChanged>>'
    TREEVIEW_SELECT = '<<TreeviewSelect>>'

    # validation
    INVALID = '<<Invalid>>'
    VALID = "<<Valid>>"
    VALIDATED = "<<Validated>>"

    # Routing
    ROUTE_DID_MOUNT = "<<RouteDidMount>>"
    ROUTE_WILL_MOUNT = "<<RouteWillMount>>"
    ROUTE_DID_UNMOUNT = "<<RouteDidUnmount>>"
    ROUTE_WILL_UNMOUNT = "<<RouteWillUnmount>>"


EventType = Union[Event, str]
