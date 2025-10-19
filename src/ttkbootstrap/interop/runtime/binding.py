"""ttkbootstrap interop: runtime binding utilities.

This module centralizes Tk/ttk event binding with a small FRP-style Stream API.

The module installs a single Tk binding per (scope, sequence) and multiplexes
to subscribers. It also provides helpers to emit virtual events with JSON
payloads and to manage rebinding safely.

Features:
  * Wraps Tk's `bind`, `bind_class`, and `bind_all` with ttkbootstrap integration.
  * Uses per-event substitution strings (`event_substring`) so Tcl only expands
    the fields each event type needs.
  * Braces `%d` substitutions as `{%d}` so JSON payloads in `event_generate -data`
    are not split by Tcl.
  * `.emit()` to programmatically generate events (virtual events carry payloads).
  * Tracks callbacks/func_ids for safe rebinding and cleanup.
  * Stream API with composition operators and Tk/domain short-circuit semantics.

Streams:
  * on(event, scope=...) -> Stream
  * Operators (return Stream): map, filter, skip_when, tap, debounce, throttle,
    cancel_when  (domain veto for pre/ING events)
  * Terminals (return Subscription): listen, then_stop, then_stop_when

Scopes:
  * "widget" (default) — bind to this widget
  * "all"             — bind application-wide
  * "<TkClassName>"   — bind to a Tk class (e.g., "TEntry")
"""

from __future__ import annotations

import weakref
from collections import defaultdict
from typing import Any, Callable, Dict, Generic, List, Literal, Mapping, Optional, TypeVar, Union

from ttkbootstrap.events import EventType
from ttkbootstrap.interop.runtime.commands import event_callback_wrapper
from ttkbootstrap.interop.spec.profiles import event_substring
from ttkbootstrap.types import Widget

# =============================================================================
# Stream primitives (minimal FRP-style layer)
# =============================================================================

T = TypeVar("T")
U = TypeVar("U")
When = Literal["now", "tail", "head", "mark"]


# --------------------------------------------------------------------- timing
class _TkScheduler:
    """Adapter around `widget.after`/`after_cancel` for time-based operators."""

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
    """Disposable handle for a stream listener."""

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
    """Minimal push-stream with composition and terminals.

    Notes:
        - Subscribers run in descending priority (higher first).
        - Returning `"break"` short-circuits later subscribers on this stream
          and signals Tk to stop propagation.
        - `cancel_when` is for domain veto on pre/ING events; `then_stop`
          controls raw Tk propagation.
    """

    __slots__ = ("_subs", "_on_empty", "_sched")

    def __init__(self, scheduler: Optional[_TkScheduler] = None):
        # store subscribers as (priority, fn)
        self._subs: List[tuple[int, Callable[[T], Any]]] = []
        self._on_empty: Optional[Callable[[], None]] = None
        self._sched = scheduler

    # ---------------- terminals ----------------------------------------------

    def listen(self, fn: Callable[[T], Any], *, priority: int = 0) -> "Subscription":
        """Subscribe a handler.

        Args:
            fn: Handler function.
            priority: Higher runs earlier (default 0).

        Returns:
            Subscription: Disposable handle.
        """
        pair = (priority, fn)
        self._subs.append(pair)
        # keep highest priority first
        self._subs.sort(key=lambda p: p[0], reverse=True)

        def _cancel():
            try:
                self._subs.remove(pair)
            finally:
                if not self._subs and self._on_empty:
                    self._on_empty()

        return Subscription(_cancel)

    def then_stop(self) -> Subscription:
        """Stop Tk propagation unconditionally (always returns 'break')."""
        return self.then_stop_when(lambda _v: True)

    def then_stop_when(self, pred: Callable[[T], bool]) -> Subscription:
        """Stop Tk propagation when predicate is true."""
        return self.listen(lambda v: "break" if pred(v) else None)

    # ---------------- operators ----------------------------------------------

    def map(self, f: Callable[[T], U]) -> "Stream[U]":
        """Transform each value via `f` and emit the result."""
        out: Stream[U] = Stream(self._sched)
        sub = self.listen(lambda v: out._next(f(v)))
        out._on_empty = lambda: sub.unlisten()
        return out

    def filter(self, pred: Callable[[T], bool]) -> "Stream[T]":
        """Emit only values for which `pred(value)` is True."""
        out: Stream[T] = Stream(self._sched)
        sub = self.listen(lambda v: out._next(v) if pred(v) else None)
        out._on_empty = lambda: sub.unlisten()
        return out

    def tap(self, fn: Callable[[T], Any]) -> "Stream[T]":
        """Invoke `fn(value)` for side-effects; forward the original value."""
        out: Stream[T] = Stream(self._sched)
        sub = self.listen(lambda v: (fn(v), out._next(v)))
        out._on_empty = lambda: sub.unlisten()
        return out

    def cancel_when(self, predicate: Callable[[T], bool], *, priority: int = 100) -> "Stream[T]":
        """Chainable domain veto for pre/ING streams.

        Installs a high-priority guard that evaluates `predicate(payload)`,
        marks the event vetoed, and returns `"break"` so later listeners (e.g.,
        the mutator) do not run. On predicate errors, fails open (no cancel).

        Args:
            predicate: Function receiving event.
            priority: Guard priority (default 100).

        Returns:
            Stream[T]: The same stream to allow fluent chaining.
        """

        def _guard(ev):
            try:
                if predicate(ev):  # <— pass event, not payload
                    payload = ev.data if hasattr(ev, "data") else ev
                    if hasattr(ev, "veto"):
                        ev.veto()
                    elif isinstance(payload, dict):
                        payload["_veto"] = True
                    return "break"
            except Exception:
                return None

        self.listen(_guard, priority=priority)
        return self

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
        """Emit after no new values arrive for `ms` ms (e.g., keystrokes)."""
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
        """Emit at most once every `ms` ms, with optional leading/trailing emits."""
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
        """Push values downstream (operators ignore 'break')."""
        for _prio, fn in list(self._subs):
            fn(v)

    # ---------- operator utilities (for cleanup and scheduling) ---------------
    def _chain(self, attach: Callable[[Callable[[T], Any]], "Subscription"], on_value: Callable[[T], Any]) -> "Stream":
        """Internal: helper to wire operator lifecycles (unused in most paths)."""
        out: Stream = Stream(self._sched)
        sub = attach(lambda v: on_value(v))
        out._on_empty = lambda: sub.unlisten()
        return out

    def _schedule(self, ms: int, fn: Callable[[], None]):
        """Internal: schedule a callback after `ms` ms."""
        if not self._sched:
            fn()
            return None
        return self._sched.call_later(ms, fn)

    def _idle(self, fn: Callable[[], None]):
        """Internal: schedule a callback at Tk idle."""
        if not self._sched:
            fn()
            return None
        return self._sched.call_idle(fn)


# =============================================================================
# Event hub (single dispatcher per (scope, sequence))
# =============================================================================

Scope = Union[Literal["widget", "all"], str]  # str = Tk class name like "TEntry"


class _EventHub:
    """Dispatcher that multiplexes a single Tk bind to stream subscribers."""

    __slots__ = ("_owner_ref", "_streams", "_func_ids")

    def __init__(self, mixin_owner: "BindingMixin") -> None:
        self._owner_ref = weakref.ref(mixin_owner)
        self._streams: Dict[tuple[str, str], Stream[Any]] = {}
        self._func_ids: Dict[tuple[str, str], str] = {}

    def on(self, sequence: str, scope: Scope) -> Stream[Any]:
        """Return (and create if needed) the Stream for (scope, sequence)."""
        scope_key = self._scope_key(scope)
        key = (scope_key, sequence)

        s = self._streams.get(key)
        if s is not None:
            return s

        owner = self._owner_ref()
        s = Stream[Any](scheduler=_TkScheduler(owner.widget))
        self._streams[key] = s

        if owner is None:
            return s

        def _dispatcher(event: Any):
            for _prio, fn in list(s._subs):
                try:
                    if fn(event) == "break":
                        return "break"
                except Exception:
                    # Optional: log
                    pass
            return None

        if scope_key == "widget":
            func_id = owner._bind_widget(sequence, _dispatcher, add=True, dedup=True)
        elif scope_key == "all":
            func_id = owner._bind_all(sequence, _dispatcher, add=True)
        else:
            func_id = owner._bind_class(scope_key, sequence, _dispatcher, add=True)

        self._func_ids[key] = func_id

        def _on_empty() -> None:
            # Keeping the dispatcher bound is cheap and avoids churn.
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
        return str(scope)


# =============================================================================
# BindingMixin
# =============================================================================


class BindingMixin:
    """Mixin that provides Tk event binding, emission, and stream access."""

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
        """Rebind all saved widget-level callbacks (e.g., after theme change)."""
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

    # TODO this needs some protection against massive payloads

    def emit(
            self,
            event: EventType,
            data: dict[str, Any] | Any | None = None,
            *,
            when: When = "now",
            **kwargs,
    ) -> None:
        """Programmatically generate a Tk event on this widget.

        Args:
            event: Tk event sequence (e.g., '<<Invalid>>', '<Return>').
            data: Payload for virtual events (<<...>>). If a mapping, it is
                merged with ``**kwargs``. If non-mapping, it is wrapped as
                ``{'data': data}`` and merged with ``**kwargs``.
            when: Tk scheduling for the generated event ('now', 'tail', 'head', 'mark').
            **kwargs: Additional key/values flattened into the payload for virtual events.
        """
        sequence = self._normalize(event)

        # Build payload depending on type of `data`
        if isinstance(data, Mapping):
            payload: Any = {**data, **kwargs} if kwargs else dict(data)
        elif data is None:
            payload = dict(kwargs) if kwargs else None
        else:
            # Non-mapping (e.g., list, tuple, str, int ...)
            payload = {"data": data, **kwargs} if kwargs else data

        # Only virtual events carry payload
        if sequence.startswith("<<") and sequence.endswith(">>") and payload is not None:
            import json
            import base64
            import datetime as _dt
            import enum as _enum

            def _default(o: Any):
                if isinstance(o, (_dt.date, _dt.datetime, _dt.time)):
                    return o.isoformat()
                if isinstance(o, _enum.Enum):
                    return getattr(o, "value", o.name)
                if isinstance(o, set):
                    return list(o)
                return str(o)

            # JSON -> base64 (avoid Tcl parsing of [, $, \, etc.)
            json_bytes = json.dumps(payload, default=_default).encode("utf-8")
            b64 = base64.b64encode(json_bytes).decode("ascii")
            self.widget.event_generate(sequence, data="b64:" + b64, when=when)
        else:
            self.widget.event_generate(sequence, when=when)

    # ---------------------------------------------------------------- helpers

    @staticmethod
    def _normalize(ev: EventType) -> str:
        """Normalize an Event or str to a Tk event sequence string."""
        return str(ev)

    # ============================================================= stream entry

    def _ensure_hub(self) -> _EventHub:
        """Create and cache the event hub on first use."""
        if self.__event_hub is None:
            self.__event_hub = _EventHub(self)
        return self.__event_hub

    def on(self, event: EventType, *, scope: Scope = "widget") -> Stream[Any]:
        """Return a multiplexed Stream for the given event and scope.

        Binding:
            The first call to `.on(event, scope)` installs a single underlying
            Tk binding for that (scope, sequence). All listeners are fanned out
            from that dispatcher. If any listener returns `"break"`, propagation
            stops for that event instance at both the stream and Tk levels.

        Args:
            event: Tk event sequence (e.g., '<<Change>>', '<Return>').
            scope: One of "widget", "all", or a Tk class name like "TEntry".

        Returns:
            Stream[Any]: Multiplexed stream for this (scope, sequence).
        """
        sequence = self._normalize(event)
        return self._ensure_hub().on(sequence, scope)

    def process_tasks(self) -> None:
        """Pump Tk's event loop once (input, timers, idles, geometry, repaints)."""
        try:
            self.widget.update()
        except Exception:
            # Widget may be destroyed or in teardown; ignore safely.
            pass

    def process_idle_tasks(self) -> None:
        """Process only idle tasks (geometry/repaint/after_idle); no user input."""
        try:
            self.widget.update_idletasks()
        except Exception:
            pass
