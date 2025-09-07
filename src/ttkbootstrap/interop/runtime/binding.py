"""
interop.runtime.binding
-----------------------

BindingMixin centralizes event binding and emission for widgets.

Features
--------
- Wraps Tk's `bind`, `bind_class`, and `bind_all` with ttkbootstrap integration.
- Uses per-event substitution strings (`event_substring`), so Tcl only expands
  the fields each event type actually needs.
- Braces `%d` substitutions as `{%d}` so JSON payloads passed via
  `event_generate -data` are not split by Tcl into multiple arguments.
- Provides `.emit()` to programmatically generate events, including
  JSON-encoded payloads for virtual events.
- Tracks registered callbacks and func_ids for safe rebinding and cleanup.

New
---
- Stream API: `.on(event, scope=...) -> Stream` with `.map()`, `.filter()`,
  and `.listen()` (aliases: `.subscribe()`, `.track()`, `.sub()`).
- `scope` may be:
    * "widget" (default) — bind to this widget (uses `bind`)
    * "all"             — bind to the application (uses `bind_all`)
    * "<TkClassName>"   — bind to a Tk class, e.g. "TEntry" (uses `bind_class`)
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic, Literal, Union

import weakref

from ttkbootstrap.interop.runtime.commands import event_callback_wrapper
from ttkbootstrap.interop.spec.profiles import event_substring
from ttkbootstrap.events import EventType
from ttkbootstrap.types import Widget

# =============================================================================
# Stream primitives (minimal FRP-style layer)
# =============================================================================

T = TypeVar("T")
U = TypeVar("U")


class Subscription:
    """Handle returned by Stream.listen(); call .unlisten() to detach."""

    __slots__ = ("_cancel", "_done")

    def __init__(self, cancel: Callable[[], None]) -> None:
        self._cancel = cancel
        self._done = False

    def unlisten(self) -> None:
        """Detach this listener."""
        if not self._done:
            try:
                self._cancel()
            finally:
                self._done = True

    # Friendly aliases for different idioms
    disconnect = unlisten
    dispose = unlisten


class Stream(Generic[T]):
    """
    Minimal push-stream supporting map/filter and listener management.

    - `listen(fn)` attaches a sink and returns a Subscription.
    - `map(f)` transforms values.
    - `filter(pred)` drops values that don't match the predicate.
    """

    __slots__ = ("_subs", "_on_empty")

    def __init__(self) -> None:
        self._subs: List[Callable[[T], None]] = []
        self._on_empty: Optional[Callable[[], None]] = None

    # --- subscription API -----------------------------------------------------

    def listen(self, fn: Callable[[T], None]) -> Subscription:
        """Attach a listener that receives each value."""
        self._subs.append(fn)

        def _cancel() -> None:
            if fn in self._subs:
                self._subs.remove(fn)
            if not self._subs and self._on_empty:
                self._on_empty()

        return Subscription(_cancel)

    # Aliases users asked for
    subscribe = listen
    track = listen
    sub = listen

    # --- operators ------------------------------------------------------------

    def map(self, f: Callable[[T], U]) -> "Stream[U]":
        """Transform each value with `f`."""
        out: Stream[U] = Stream()
        self.listen(lambda v: out._next(f(v)))
        return out

    def filter(self, pred: Callable[[T], bool]) -> "Stream[T]":
        """Only pass values for which `pred(value)` is True."""
        out: Stream[T] = Stream()
        self.listen(lambda v: out._next(v) if pred(v) else None)
        return out

    # --- internal -------------------------------------------------------------

    def _next(self, v: T) -> None:
        # Snapshot to tolerate unsubscription during iteration
        for fn in list(self._subs):
            fn(v)


# =============================================================================
# Event hub (single dispatcher per (scope, sequence))
# =============================================================================

Scope = Union[Literal["widget", "all"], str]  # str = Tk class name like "TEntry"


class _EventHub:
    """
    One dispatcher per (scope, sequence).

    Reuses BindingMixin.bind/bind_class/bind_all so per-event substitution and
    func_id tracking remain exactly as in the existing system.
    """

    __slots__ = ("_owner_ref", "_streams", "_func_ids")

    def __init__(self, mixin_owner: "BindingMixin") -> None:
        self._owner_ref = weakref.ref(mixin_owner)
        # Key by (scope, sequence) so widget/class/all namespaces don't collide
        self._streams: Dict[tuple[str, str], Stream[Any]] = {}
        self._func_ids: Dict[tuple[str, str], str] = {}

    def on(self, sequence: str, scope: Scope) -> Stream[Any]:
        scope_key = self._scope_key(scope)
        key = (scope_key, sequence)

        s = self._streams.get(key)
        if s is not None:
            return s

        owner = self._owner_ref()
        s = Stream[Any]()
        self._streams[key] = s

        if owner is None:
            # Owner is gone; return inert stream
            return s

        # Single Tk binding → fan out to all listeners of this stream
        def _dispatcher(event: Any) -> None:
            # Whatever event_callback_wrapper provides is forwarded as payload
            s._next(event)

        # Route to the correct underlying binder
        if scope_key == "widget":
            func_id = owner.bind(sequence, _dispatcher, add=True, dedup=True)
        elif scope_key == "all":
            func_id = owner.bind_all(sequence, _dispatcher, add=True)
        else:
            # scope_key is a Tk class name
            func_id = owner.bind_class(scope_key, sequence, _dispatcher, add=True)

        self._func_ids[key] = func_id

        # Optional: remove our stream record when last listener goes away
        def _on_empty() -> None:
            # Keeping the dispatcher bound is cheap and avoids churn.
            # If you want strict cleanup, you could unbind here by rebuilding
            # the Tcl binding script without `func_id`.
            self._streams.pop(key, None)

        s._on_empty = _on_empty
        return s

    @staticmethod
    def _scope_key(scope: Scope) -> str:
        """Normalize scope to a string key."""
        if scope == "widget":
            return "widget"
        if scope == "all":
            return "all"
        # Otherwise assume it's a Tk class name like "TEntry"
        return str(scope)


# =============================================================================
# BindingMixin
# =============================================================================


class BindingMixin:
    """Mixin providing Tk event binding and emission helpers."""

    widget: Widget

    def __init__(self, *args, **kwargs):
        # sequence -> list of func_ids
        self.__tcl_bound_events: dict[str, list[str]] = defaultdict(list)
        # func_id -> Python callable
        self.__tcl_callbacks: dict[str, Callable[..., Any]] = {}
        # lazy-initialized hub for stream events
        self.__event_hub: Optional[_EventHub] = None
        super().__init__(*args, **kwargs)

    # ------------------------------------------------------------------ binders

    def bind(
            self,
            event: EventType,
            func: Callable,
            *,
            add: bool = True,
            dedup: bool = False,
    ) -> str:
        """Bind a callback for this widget with per-event substitutions."""
        sequence = self._normalize(event)
        func_id = event_callback_wrapper(self.widget, func, sequence, dedup=dedup)
        subs = event_substring(sequence).replace("%d", "{%d}")
        script = f"{func_id} {subs}"
        self.widget.tk.call(
            "bind", str(self.widget), sequence, f"+{script}" if add else script
        )
        self.__tcl_bound_events[sequence].append(func_id)
        self.__tcl_callbacks[func_id] = func
        return func_id  # :contentReference[oaicite:2]{index=2}

    def bind_class(
            self,
            class_name: str,
            event: EventType,
            func: Callable,
            *,
            add: bool = True,
    ) -> str:
        """Bind a callback for all widgets of a given Tk class."""
        sequence = self._normalize(event)
        func_id = event_callback_wrapper(self.widget, func, sequence)
        subs = event_substring(sequence).replace("%d", "{%d}")
        script = f"{func_id} {subs}"
        self.widget.tk.call(
            "bind", class_name, sequence, f"+{script}" if add else script
        )
        self.__tcl_bound_events[sequence].append(func_id)
        self.__tcl_callbacks[func_id] = func
        return func_id

    def bind_all(
            self,
            event: EventType,
            func: Callable,
            *,
            add: bool = True,
    ) -> str:
        """Bind a callback for all widgets in the application."""
        sequence = self._normalize(event)
        func_id = event_callback_wrapper(self.widget, func, sequence)
        subs = event_substring(sequence).replace("%d", "{%d}")
        script = f"{func_id} {subs}"
        self.widget.tk.call("bind", "all", sequence, f"+{script}" if add else script)
        self.__tcl_bound_events[sequence].append(func_id)
        self.__tcl_callbacks[func_id] = func
        return func_id

    # ---------------------------------------------------------------- rebinders

    def _tcl_rebind_widget(self) -> None:
        """Rebind all saved widget-level callbacks (e.g. after theme change)."""
        for sequence, func_ids in self.__tcl_bound_events.items():
            for func_id in func_ids:
                subs = event_substring(sequence).replace("%d", "{%d}")
                script = f"{func_id} {subs}"
                self.widget.tk.call("bind", str(self.widget), sequence, script)

    def _tcl_rebind_class(self, class_name: str) -> None:
        """Rebind all saved class-level callbacks."""
        for sequence, func_ids in self.__tcl_bound_events.items():
            for func_id in func_ids:
                subs = event_substring(sequence).replace("%d", "{%d}")
                script = f"{func_id} {subs}"
                self.widget.tk.call("bind", class_name, sequence, script)

    def _tcl_rebind_all(self) -> None:
        """Rebind all saved global callbacks."""
        for sequence, func_ids in self.__tcl_bound_events.items():
            for func_id in func_ids:
                subs = event_substring(sequence).replace("%d", "{%d}")
                script = f"{func_id} {subs}"
                self.widget.tk.call("bind", "all", sequence, script)

    # ---------------------------------------------------------------- emitters

    def emit(self, event: EventType, data: dict[str, Any] | None = None, **kwargs) -> None:
        """
        Programmatically generate a Tk event on this widget.

        Parameters
        ----------
        event : EventType
            The event sequence (e.g., <<Invalid>>, <Return>).
        data : dict | None
            Optional dict payload.
        **kwargs
            Other Arbitrary key-value pairs to flatten into event.data.
        """
        sequence = self._normalize(event)

        # Flatten data + kwargs into one payload
        payload: dict[str, Any] = {}
        if data:
            payload.update(data)
        if kwargs:
            payload.update(kwargs)

        if sequence.startswith("<<") and sequence.endswith(">>") and payload:
            import json

            self.widget.event_generate(sequence, data=json.dumps(payload))
        else:
            self.widget.event_generate(sequence)

    # ---------------------------------------------------------------- helpers

    @staticmethod
    def _normalize(ev: EventType) -> str:
        """Normalize an Event or str to a Tk event sequence string."""
        return str(ev)  #

    # ============================================================= stream entry

    def _ensure_hub(self) -> _EventHub:
        """Lazy-create (and cache) the event hub used by `on()`."""
        if self.__event_hub is None:
            self.__event_hub = _EventHub(self)
        return self.__event_hub

    def on(self, event: EventType, *, scope: Scope = "widget") -> Stream[Any]:
        """
        Create (or reuse) a Stream for the given Tk event sequence and scope.

        Parameters
        ----------
        event : EventType
            The event sequence (e.g., <<Change>>, <Return>, <KeyRelease>).
        scope : "widget" | "all" | str (Tk class name)
            "widget" (default) binds to this widget,
            "all" binds to the application,
            "<TkClassName>" binds to a Tk class, e.g. "TEntry".

        Notes
        -----
        - This does a single underlying Tk `bind` per (scope, sequence) and
          multiplexes to all listeners of the returned Stream.
        - Internally routes to `.bind`, `.bind_all`, or `.bind_class`.
        """
        sequence = self._normalize(event)
        return self._ensure_hub().on(sequence, scope)
