from enum import StrEnum
from typing import Any, Callable, Optional
from inspect import Signature, Parameter


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

    WINDOW_ACTIVATED = "<<Activate>>"
    WINDOW_DEACTIVATED = "<<Deactivate>>"
    MENU_SELECTED = "<<MenuSelected>>"
    SELECTION = "<<Selection>>"
    SELECTED = "<<Selected>>"
    DESELECTED = "<<Deselected>>"
    COMBOBOX_SELECTED = "<<ComboboxSelected>>"
    INCREMENT = "<<Increment>>"
    DECREMENT = "<<Decrement>>"
    DELETE = "<<Delete>>"
    NOTEBOOK_TAB_CHANGED = "<<NotebookTabChanged>>"
    INPUT_METHOD_CHANGED = '<<IMChanged>>'
    TREEVIEW_SELECT = '<<TreeviewSelect>>'

    # validation
    INVALID = '<<Invalid>>'
    VALID = "<<Valid>>"
    VALIDATED = "<<Validated>>"

    # navigation
    PAGE_WILL_MOUNT = "<<PageWillMount>>"
    PAGE_MOUNTED = "<<PageMounted>>"
    PAGE_UNMOUNTED = "<<PageUnmounted>>"
    PAGE_CHANGED = '<<PageChanged>>'


# -------- bound callable shown on instances: btn.on_click(...) --------
class _BoundEventMethod:
    def __init__(self, owner: Any, name: str, seq: str, *, replace: bool, dedup: bool, doc: str):
        self._owner, self._name, self._seq = owner, name, seq
        self._replace, self._dedup = replace, dedup
        self.__doc__ = doc
        self.__signature__ = Signature(  # type: ignore[attr-defined]
            parameters=[Parameter(
                "handler", Parameter.POSITIONAL_OR_KEYWORD,
                default=None, annotation=Optional[Callable[[Any], Any]])],
            return_annotation=type(owner).__name__,
        )

    def __call__(self, handler: Optional[Callable[[Any], Any]] = None):
        if handler is None:
            return getattr(self._owner, f"__{self._name}_handler", None)
        if not callable(handler):
            raise TypeError(f"{self._name} expects a callable or None")

        old_id = getattr(self._owner, f"__{self._name}_fid", None)
        if old_id and self._replace and hasattr(self._owner, "unbind"):
            self._owner.unbind(self._seq, func_id=old_id)

        fid = self._owner.bind(self._seq, handler, add=True, dedup=self._dedup)
        setattr(self._owner, f"__{self._name}_fid", fid)
        setattr(self._owner, f"__{self._name}_handler", handler)
        return self._owner  # chainable


# -------- private descriptor; factory returns an instance of this --------
class _EventMethodDescriptor:
    def __init__(self, event: Any, *, replace: bool, dedup: bool, doc: str | None):
        self._event, self._replace, self._dedup, self._doc = event, replace, dedup, doc
        self._name: str | None = None
        self._seq: str | None = None

    def __call__(self, fn: Callable):
        # grab docstring from the dummy method if not provided
        if self._doc is None and fn.__doc__:
            self._doc = fn.__doc__
        return self  # descriptor itself replaces the function

    def __set_name__(self, owner, name: str):
        self._name = name
        self._seq = self._normalize(self._event)
        self.__doc__ = self._doc or f"{name}(handler: Optional[Callable]) -> {owner.__name__}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self._name is None or self._seq is None:
            raise RuntimeError("event_handler used before __set_name__")
        return _BoundEventMethod(
            instance, self._name, self._seq,
            replace=self._replace, dedup=self._dedup, doc=self.__doc__ or "",
        )

    @staticmethod
    def _normalize(ev: Any) -> str:
        try:
            if isinstance(ev, Event):
                return str(ev)
        except Exception:
            pass
        if isinstance(ev, str):
            return ev
        raise TypeError(f"Unsupported event: {ev!r}")


# -------- snake_case public API --------
def event_handler(event: Any, *, replace: bool = True, dedup: bool = True, doc: str | None = None):
    """Decorator factory for Tk-style on_* methods.

    Usage:
        @event_handler(Event.ON_CLICK)
        def on_click(self, event): ...
    """
    return _EventMethodDescriptor(event, replace=replace, dedup=dedup, doc=doc)
