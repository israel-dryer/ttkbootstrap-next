"""
ttkbootstrap.events
-------------------

Fluent event binding utilities and the `Event` string-enum.

This module provides:

- **Event (StrEnum)** — canonical Tk/Tkinter event strings (e.g., "<Return>", "<<Change>>").
- **@event_handler(...)** — a decorator that turns a method into a *fluent*
  getter/setter for a single event **and** an optional *pre-processor*:

  Fluent API (instance level)
  ---------------------------
  • `on_change()`              → get the current user handler or `None`
  • `on_change(fn)`            → set user handler (returns the widget for chaining)
  • `on_change(None)`          → clear user handler (returns the widget)

  Pre-processor (method body)
  ---------------------------
  The decorated function’s *body* runs **before** the user handler and may:
  - return `"skip"` (any case) → do **not** call the user handler
  - return `"break"`           → stop Tk event propagation (Tk convention)
  - return `None`              → pass the original Tk event to the user handler
  - return `<value>`           → pass `<value>` to the user handler instead

Binding & Rebinding
-------------------
- `replace=True` (default): if a prior binding exists, unbind it before rebinding.
- `dedup=True` (default): request de-duplicated binding in the underlying `bind(...)`.

This pattern keeps the public API fluent while making it explicit that the decorated
method can act as a transform hook for the event payload.
"""

from enum import StrEnum
from typing import Any, Callable, Optional, Union
from inspect import Signature, Parameter

Transform = Union[Callable[[Any, Any], Any], str]  # (self, event) -> new | None | "skip" | "break"


class Event(StrEnum):
    """Canonical Tk/Tkinter event strings (keyboard, mouse, virtual, etc.)."""

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
    def __init__(
            self, owner: Any, name: str, seq: str,
            *, replace: bool, dedup: bool, doc: str,
            processor: Optional[Callable[[Any, Any], Any]],
            transform_spec: Optional[Transform]):
        self._owner, self._name, self._seq = owner, name, seq
        self._replace, self._dedup = replace, dedup
        self._processor = processor  # fallback processor (from method body)
        self._transform_spec = transform_spec  # decorator-provided transform (callable or str)
        self.__doc__ = doc
        self.__signature__ = Signature(  # type: ignore[attr-defined]
            parameters=[Parameter(
                "handler", Parameter.POSITIONAL_OR_KEYWORD,
                default=None, annotation=Optional[Callable[[Any], Any]])],
            return_annotation=type(owner).__name__,
        )

    def __call__(self, handler: Optional[Callable[[Any], Any]] = None):
        # getter
        if handler is None:
            return getattr(self._owner, f"__{self._name}_handler", None)

        if not callable(handler):
            raise TypeError(f"{self._name} expects a callable or None")

        # (re)bind with a dispatcher that can pre-process
        old_id = getattr(self._owner, f"__{self._name}_fid", None)
        if old_id and self._replace and hasattr(self._owner, "unbind"):
            self._owner.unbind(self._seq, func_id=old_id)

        def _resolve_transform():
            """
            Choose the active transform:
              1) decorator-provided `transform=...` (callable or method name)
              2) else the original method body (`self._processor`)
              3) else None
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
                # ---- control tokens (string-based) ---------------------
                if isinstance(out, str):
                    if out.lower() == "skip":  # do not call user handler
                        return None
                    if out == "break":  # Tk convention: stop propagation
                        return "break"
                # --------------------------------------------------------
                if out is not None:
                    e = out  # transformed payload for user handler
            return handler(e)

        fid = self._owner.bind(self._seq, dispatcher, add=True, dedup=self._dedup)
        setattr(self._owner, f"__{self._name}_fid", fid)
        setattr(self._owner, f"__{self._name}_handler", handler)
        return self._owner  # chainable


class _EventMethodDescriptor:
    def __init__(self, event: Any, *, replace: bool, dedup: bool, doc: str | None, transform: Optional[Transform]):
        self._event, self._replace, self._dedup, self._doc = event, replace, dedup, doc
        self._name: str | None = None
        self._seq: str | None = None
        self._processor: Optional[Callable[[Any, Any], Any]] = None  # original method body
        self._transform_spec: Optional[Transform] = transform  # decorator arg

    def __call__(self, fn: Callable[[Any, Any], Any]):
        # capture docstring; method body remains a processor *if* no transform was provided
        if self._doc is None and getattr(fn, "__doc__", None):
            self._doc = fn.__doc__
        if self._transform_spec is None:
            self._processor = fn  # preserve old behavior
        # else: transform=... overrides body; body is kept only for docs
        return self

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
            replace=self._replace, dedup=self._dedup,
            doc=self.__doc__ or "",
            processor=self._processor,
            transform_spec=self._transform_spec,
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


def event_handler(
        event: Any,
        *,
        replace: bool = True,
        dedup: bool = True,
        doc: str | None = None,
        transform: Optional[Transform] = None,
):
    """Decorator that creates a Tk-style on_* method with optional pre-processing.

    Pre-processing order (first match wins):
      1) `transform=` argument passed to the decorator
         - callable: (self, event) -> new | None | "skip" | "break"
         - str: name of an instance method with that signature
      2) the decorated function body (legacy behavior, kept for convenience)
      3) no pre-processing

    The decorated function's body (if effective) follows this contract:
      - return "skip" (any case) → do NOT call the user handler
      - return "break"           → stop Tk event propagation
      - return None              → pass the original event to the user handler
      - return <value>           → pass <value> to the user handler instead of the event
    """
    return _EventMethodDescriptor(event, replace=replace, dedup=dedup, doc=doc, transform=transform)


# Public alias
EventType = Union[Event, str]
