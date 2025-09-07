"""
ttkbootstrap.events
-------------------

Fluent event binding utilities and the `Event` string-enum.

- `Event` (StrEnum): canonical Tk/Tkinter event strings (e.g., "<Return>", "<<Change>>").
- `@event_handler(...)`: turns a method into a fluent getter/setter for one event,
  with an optional pre-dispatch `transform` hook.

Fluent API (instance level)
---------------------------
• `on_change()`           → get current user handler (or None)
• `on_change(fn)`         → set user handler (returns the widget for chaining)
• `on_change(None)`       → clear user handler (unbinds; returns the widget)

Pre-dispatch transform
----------------------
Provide a `transform` in the decorator (callable or method name) or define
a method body (used as a fallback). Transform contract:

    (self, event) -> new_event | None | "skip" | "break"

- "skip"   → do not call the user handler
- "break"  → stop Tk event propagation
- None     → pass the original event through
- other    → pass that value to the user handler instead of the event
"""

from __future__ import annotations

from enum import StrEnum
from inspect import Parameter, Signature
from typing import Any, Callable, Optional, Union

__all__ = ["Event", "event_handler", "EventType"]

Transform = Union[Callable[[Any, Any], Any], str]  # (self, event) -> new | None | "skip" | "break"
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
    CHANGE = "<<Change>>"
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
    INPUT_METHOD_CHANGED = "<<IMChanged>>"
    TREEVIEW_SELECT = "<<TreeviewSelect>>"

    # Validation
    INVALID = "<<Invalid>>"
    VALID = "<<Valid>>"
    VALIDATED = "<<Validated>>"

    # Navigation
    PAGE_WILL_MOUNT = "<<PageWillMount>>"
    PAGE_MOUNTED = "<<PageMounted>>"
    PAGE_UNMOUNTED = "<<PageUnmounted>>"
    PAGE_CHANGED = "<<PageChanged>>"


# --------------------------- Fluent event method machinery ---------------------------

_UNSET = object()  # sentinel to distinguish "getter" call from "clear (None)"


class _BoundEventMethod:
    """
    Per-instance, callable façade for a fluent event method.

    - `bound()`           → getter
    - `bound(fn)`         → setter (binds and stores `fn`)
    - `bound(None)`       → clear (unbinds) and return owner
    """

    def __init__(
            self,
            owner: Any,
            name: str,
            seq: str,
            *,
            replace: bool,
            dedup: bool,
            doc: str,
            processor: Optional[Callable[[Any, Any], Any]],
            transform_spec: Optional[Transform],
    ):
        self._owner, self._name, self._seq = owner, name, seq
        self._replace, self._dedup = replace, dedup
        self._processor = processor  # fallback transform from method body
        self._transform_spec = transform_spec  # decorator-provided transform
        self.__doc__ = doc
        # Public-looking signature for IDEs/help (shows Optional[Callable] with default None)
        self.__signature__ = Signature(  # type: ignore[attr-defined]
            parameters=[
                Parameter(
                    "handler",
                    Parameter.POSITIONAL_OR_KEYWORD,
                    default=None,
                    annotation=Optional[Callable[[Any], Any]],
                )
            ],
            return_annotation=type(owner).__name__,
        )

    def __call__(self, handler=_UNSET):
        # Getter
        if handler is _UNSET:
            return getattr(self._owner, f"__{self._name}_handler", None)

        # Clear
        if handler is None:
            old_id = getattr(self._owner, f"__{self._name}_fid", None)
            if old_id and hasattr(self._owner, "unbind"):
                try:
                    self._owner.unbind(self._seq, func_id=old_id)
                except Exception:
                    pass
            setattr(self._owner, f"__{self._name}_fid", None)
            setattr(self._owner, f"__{self._name}_handler", None)
            return self._owner

        # Set
        if not callable(handler):
            raise TypeError(f"{self._name} expects a callable, None, or no argument")

        # (Re)bind with a dispatcher that can pre-process
        old_id = getattr(self._owner, f"__{self._name}_fid", None)
        if old_id and self._replace and hasattr(self._owner, "unbind"):
            try:
                self._owner.unbind(self._seq, func_id=old_id)
            except Exception:
                pass

        def _resolve_transform():
            """
            Pick the active transform:
              1) decorator-provided `transform=...` (callable or method name)
              2) method body (`self._processor`)
              3) None
            """
            spec = self._transform_spec
            if isinstance(spec, str):
                return getattr(self._owner, spec, None)  # instance method by name
            if callable(spec):
                return lambda e, _fn=spec: _fn(self._owner, e)  # bind self
            return self._processor

        def dispatcher(evt: Any):
            e = evt
            xform = _resolve_transform()
            if xform is not None:
                out = xform(evt)
                if isinstance(out, str):
                    s = out.lower()
                    if s == "skip":
                        return None
                    if out == "break":  # preserve Tk "break" exact token
                        return "break"
                if out is not None:
                    e = out
            return handler(e)

        fid = self._owner.bind(self._seq, dispatcher, add=True, dedup=self._dedup)
        setattr(self._owner, f"__{self._name}_fid", fid)
        setattr(self._owner, f"__{self._name}_handler", handler)
        return self._owner  # chainable


class _EventMethodDescriptor:
    """Descriptor created by @event_handler that exposes a fluent event method."""

    def __init__(
            self,
            event: Any,
            *,
            replace: bool,
            dedup: bool,
            doc: str | None,
            transform: Optional[Transform],
    ):
        self._event, self._replace, self._dedup, self._doc = event, replace, dedup, doc
        self._name: str | None = None
        self._seq: str | None = None
        self._processor: Optional[Callable[[Any, Any], Any]] = None  # optional method-body transform
        self._transform_spec: Optional[Transform] = transform  # decorator arg

    def __call__(self, fn: Callable[[Any, Any], Any]):
        # Capture docstring; use body as transform only if no transform= was provided.
        if self._doc is None and getattr(fn, "__doc__", None):
            self._doc = fn.__doc__
        if self._transform_spec is None:
            self._processor = fn
        return self  # replace the method with the descriptor

    def __set_name__(self, owner, name: str):
        self._name = name
        self._seq = self._normalize(self._event)
        self.__doc__ = self._doc or f"{name}(handler: Optional[Callable]) → {owner.__name__}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self._name is None or self._seq is None:
            raise RuntimeError("event_handler used before __set_name__")
        return _BoundEventMethod(
            instance,
            self._name,
            self._seq,
            replace=self._replace,
            dedup=self._dedup,
            doc=self.__doc__ or "",
            processor=self._processor,
            transform_spec=self._transform_spec,
        )

    @staticmethod
    def _normalize(ev: Any) -> str:
        # Accept Event or str; avoid importing anything outside this module.
        if isinstance(ev, Event):
            return str(ev)
        if isinstance(ev, str):
            return ev
        raise TypeError(f"Unsupported event: {ev!r}")


def event_handler(
        event: Any,
        *,
        replace: bool = True,
        dedup: bool = True,
        doc: str | None = None,
        transform: Optional[Transform] = None,
):
    """
    Decorator that creates a Tk-style fluent `on_*` method with optional pre-processing.

    Transform resolution (first match wins):
      1) `transform=` argument (callable or method name on the instance)
      2) the decorated function body (legacy convenience)
      3) no transform

    See the module docstring for the transform contract.
    """
    return _EventMethodDescriptor(event, replace=replace, dedup=dedup, doc=doc, transform=transform)
