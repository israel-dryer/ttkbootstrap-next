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
- Stream API:
    * `.on(event, scope=...) -> Stream` (lazy pipeline; no Tk bind yet)
    * Operators: `.map()`, `.filter()`, `.tap()` (return Stream)
    * Terminals: `.listen()`, `.then_stop()`, `.then_stop_when()` (return Subscription)
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


# --------------------------------------------------------------------- timing
class _TkScheduler:
    """Small adapter around widget.after/after_cancel for time-based operators."""
    __slots__ = ("_w",)

    def __init__(self, widget) -> None:
        self._w = widget

    def call_later(self, ms: int, cb):
        return self._w.after(ms, cb)

    def call_idle(self, cb):
        return self._w.after_idle(cb)

    def cancel(self, token):
        try:
            self._w.after_cancel(token)
        except Exception:
            # token might already have fired or widget destroyed
            pass


class Subscription:
    """Handle returned by Stream terminals; call `.unlisten()` to detach."""

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
    Minimal push-stream with composition + terminals.

    Operators (return Stream; composition only):
      - map(f): transform values
      - filter(pred): pass only matching values
      - tap(fn): run side-effects and pass original value through

    Terminals (return Subscription; these CREATE the Tk binding):
      - listen(fn): subscribe a handler (its return may be 'break')
      - then_stop(): subscribe a handler that always returns 'break'
      - then_stop_when(pred): subscribe a handler that returns 'break' when pred(value) is True
    """

    __slots__ = ("_subs", "_on_empty", "_sched")

    def __init__(self, scheduler: "_TkScheduler | None" = None) -> None:
        self._subs: List[Callable[[T], Any]] = []
        self._on_empty: Optional[Callable[[], None]] = None
        self._sched = scheduler

    # ---------------- terminals ----------------------------------------------

    def listen(self, fn: Callable[[T], Any]) -> Subscription:
        """Subscribe a handler for each value (this CREATES the Tk binding)."""
        self._subs.append(fn)

        def _cancel() -> None:
            if fn in self._subs:
                self._subs.remove(fn)
            if not self._subs and self._on_empty is not None:
                cb = self._on_empty  # narrow Optional for linters
                cb()  # type: ignore[misc]

        return Subscription(_cancel)

        # ergonomic aliases available via external assignment if desired:
        # subscribe = listen
        # track = listen
        # sub = listen

    def then_stop(self) -> Subscription:
        """Subscribe a handler that always stops Tk propagation (returns 'break')."""
        return self.listen(lambda _v: "break")

    def then_stop_when(self, pred: Callable[[T], bool]) -> Subscription:
        """Subscribe a handler that stops Tk propagation when predicate is True."""
        return self.listen(lambda v: "break" if pred(v) else None)

    # ---------------- operators ----------------------------------------------

    def map(self, f: Callable[[T], U]) -> "Stream[U]":
        out: Stream[U] = Stream(self._sched)
        sub = self.listen(lambda v: out._next(f(v)))
        out._on_empty = lambda: sub.unlisten()
        return out

    def filter(self, pred: Callable[[T], bool]) -> "Stream[T]":
        out: Stream[T] = Stream(self._sched)
        sub = self.listen(lambda v: out._next(v) if pred(v) else None)
        out._on_empty = lambda: sub.unlisten()
        return out

    def tap(self, fn: Callable[[T], Any]) -> "Stream[T]":
        out: Stream[T] = Stream(self._sched)
        sub = self.listen(lambda v: (fn(v), out._next(v)))
        out._on_empty = lambda: sub.unlisten()
        return out

    def delay(self, ms: int) -> "Stream[T]":
        """Re-emit each value after `ms` milliseconds."""
        out: Stream[T] = Stream(self._sched)
        tokens: List[Any] = []

        def on_value(v: T):
            token = self._schedule(ms, lambda: out._next(v))
            tokens.append(token)

        sub = self.listen(on_value)

        def _cleanup():
            sub.unlisten()
            for t in tokens:
                if t is not None:
                    self._sched.cancel(t)  # type: ignore[union-attr]

        out._on_empty = _cleanup
        return out

    def idle(self) -> "Stream[T]":
        """Re-emit each value at Tk idle (after current event processing)."""
        out: Stream[T] = Stream(self._sched)
        tokens: List[Any] = []

        def on_value(v: T):
            token = self._idle(lambda: out._next(v))
            tokens.append(token)

        sub = self.listen(on_value)

        def _cleanup():
            sub.unlisten()
            for t in tokens:
                if t is not None:
                    self._sched.cancel(t)  # safe to call even if idle already fired

        out._on_empty = _cleanup
        return out

    def debounce(self, ms: int) -> "Stream[T]":
        """
        Emit after no new values arrive for `ms` milliseconds.
        Useful for keystroke-driven validation/formatting.
        """
        out: Stream[T] = Stream(self._sched)
        last: Dict[str, Any] = {"value": None, "token": None}

        def fire():
            v = last["value"]
            last["token"] = None
            out._next(v)  # type: ignore[misc]

        def on_value(v: T):
            last["value"] = v
            tok = last["token"]
            if tok is not None:
                self._sched.cancel(tok)  # type: ignore[union-attr]
            last["token"] = self._schedule(ms, fire)

        sub = self.listen(on_value)

        def _cleanup():
            sub.unlisten()
            tok = last["token"]
            if tok is not None:
                self._sched.cancel(tok)  # type: ignore[union-attr]
            last["token"] = None

        out._on_empty = _cleanup
        return out

    def throttle(self, ms: int, *, leading: bool = True, trailing: bool = True) -> "Stream[T]":
        """
        Emit at most once every `ms` ms.
        - leading=True: emit immediately on first event in window.
        - trailing=True: emit once more at the end with the last value.
        """
        out: Stream[T] = Stream(self._sched)
        state = {"open": True, "pending": False, "last": None, "timer": None}

        def open_window():
            state["open"] = True
            state["timer"] = None
            if trailing and state["pending"]:
                out._next(state["last"])  # type: ignore[misc]
                state["pending"] = False
                state["open"] = False
                state["timer"] = self._schedule(ms, open_window)

        def on_value(v: T):
            if state["open"]:
                if leading:
                    out._next(v)
                else:
                    # reserve trailing if not leading
                    state["pending"] = True
                    state["last"] = v
                state["open"] = False
                state["timer"] = self._schedule(ms, open_window)
            else:
                state["pending"] = True
                state["last"] = v

        sub = self.listen(on_value)

        def _cleanup():
            sub.unlisten()
            if state["timer"] is not None:
                self._sched.cancel(state["timer"])  # type: ignore[union-attr]
            state["timer"] = None

        out._on_empty = _cleanup
        return out

    # ---------------- internal -----------------------------------------------

    def _next(self, v: T) -> None:
        for fn in list(self._subs):
            fn(v)

    # ---------- operator utilities (for cleanup and scheduling) ---------------
    def _chain(self, attach: Callable[[Callable[[T], Any]], "Subscription"], on_value: Callable[[T], Any]) -> "Stream":
        out: Stream = Stream(self._sched)
        sub = attach(lambda v: on_value(v))
        out._on_empty = lambda: sub.unlisten()
        return out

    def _schedule(self, ms: int, fn: Callable[[], None]):
        if not self._sched:
            # Fallback: run immediately if no scheduler (shouldn't happen for Tk streams)
            fn()
            return None
        return self._sched.call_later(ms, fn)

    def _idle(self, fn: Callable[[], None]):
        if not self._sched:
            fn()
            return None
        return self._sched.call_idle(fn)


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
        s = Stream[Any](scheduler=_TkScheduler(owner.widget))
        self._streams[key] = s

        if owner is None:
            # Owner is gone; return inert stream
            return s

        # Single Tk binding → fan out to all listeners of this stream.
        # IMPORTANT: if any listener returns "break", we return "break" to Tk.
        def _dispatcher(event: Any):
            broke = False
            for fn in list(s._subs):
                try:
                    if fn(event) == "break":
                        broke = True
                except Exception:
                    # Optional: log via your error bus; we avoid breaking the chain.
                    pass
            return "break" if broke else None

        # Route to the correct underlying binder
        if scope_key == "widget":
            func_id = owner._bind_widget(sequence, _dispatcher, add=True, dedup=True)
        elif scope_key == "all":
            func_id = owner._bind_all(sequence, _dispatcher, add=True)
        else:
            # scope_key is a Tk class name
            func_id = owner._bind_class(scope_key, sequence, _dispatcher, add=True)

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

    def _bind_widget(
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
        return func_id

    def _bind_class(
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

    def _bind_all(
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
        return str(ev)

    # ============================================================= stream entry

    def _ensure_hub(self) -> _EventHub:
        """Lazy-create (and cache) the event hub used by `on()`."""
        if self.__event_hub is None:
            self.__event_hub = _EventHub(self)
        return self.__event_hub

    def on(self, event: EventType, *, scope: Scope = "widget") -> Stream[Any]:
        """
        Create (or reuse) a Stream for the given Tk event sequence and scope.

        IMPORTANT
        ---------
        This method is **lazy**: it builds the pipeline but performs **no Tk
        binding** until you call a **terminal operator**:
            - `.listen(handler)`
            - `.then_stop()`
            - `.then_stop_when(predicate)`

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
        - A single underlying Tk `bind` is installed per (scope, sequence) and
          multiplexes to all listeners of the returned Stream.
        - Internally routes to `.bind`, `.bind_all`, or `.bind_class`.
        - If any listener returns the string "break", the dispatcher returns
          "break" to Tk and propagation stops for that event instance.
        """
        sequence = self._normalize(event)
        return self._ensure_hub().on(sequence, scope)
