import json
import weakref
from collections import defaultdict
from tkinter import ttk
from typing import Any, Callable

from ttkbootstrap.interop.aliases import EVENT_ALIASES
from ttkbootstrap.interop.substitutions import get_event_substring
from ttkbootstrap.interop.commands import event_callback_wrapper


class BindingMixin:
    """Mixin that provides alias-aware event binding with substitution-based parsing.

    Uses Tcl-level event binding to support advanced substitutions (e.g., %d for data).
    Automatically wraps event handlers with converters and tracks bindings via weakrefs.
    """

    widget: ttk.Widget
    _bound_events: dict[str, list[str]]
    _callbacks: weakref.WeakValueDictionary[str, Callable]

    def __init__(self):
        """Initialize the binding mixin with weak reference tracking."""
        self._bound_events = defaultdict(list)
        self._callbacks = weakref.WeakValueDictionary()

    @staticmethod
    def _normalize(event: str) -> str:
        """Convert alias to a full Tk event sequence."""
        return event if ("<<" in event or "<" in event) else EVENT_ALIASES.get(event, f"<<{event}>>")

    def bind(self, event: str, func: Callable, *, add: bool = True, dedup: bool = False) -> str:
        """Bind a callback to an event using Tcl substitution (e.g., %d for data).

        Args:
            event: Event alias or full sequence (e.g., 'click', '<<MyEvent>>').
            func: The callback to bind.
            add: Whether to add to existing handlers.
            dedup: If True, deduplicate based on `id(func)`.

        Returns:
            func_id: The internal Tcl function ID.
        """
        sequence = self._normalize(event)
        func_id = event_callback_wrapper(self.widget, func, sequence, dedup=dedup)
        script = f"{func_id} {get_event_substring()}"

        self.widget.tk.call("bind", str(self.widget), sequence, f"+{script}" if add else script)
        self._bound_events[sequence].append(func_id)
        self._callbacks[func_id] = func
        return func_id

    def bind_class(self, class_name: str, event: str, func: Callable, *, add: bool = True, dedup: bool = False) -> str:
        """Bind a callback to a widget class using alias-aware wrapping."""
        sequence = self._normalize(event)
        func_id = event_callback_wrapper(self.widget, func, sequence, dedup=dedup)
        script = f"{func_id} {get_event_substring()}"
        self.widget.bind_class(class_name, sequence, f"+{script}" if add else script)
        self._bound_events[f"class::{class_name}::{sequence}"].append(func_id)
        self._callbacks[func_id] = func
        return func_id

    def unbind_class(self, class_name: str, event: str, func_id: str | None = None):
        """Unbind one or all handlers for a class-level binding."""
        sequence = self._normalize(event)
        key = f"class::{class_name}::{sequence}"
        current_ids = self._bound_events.get(key, [])

        if func_id:
            if func_id in current_ids:
                current_ids.remove(func_id)
                self._callbacks.pop(func_id, None)
        else:
            for fid in current_ids:
                self._callbacks.pop(fid, None)
            current_ids.clear()

        self.widget.bind_class(class_name, sequence, "")
        for fid in current_ids:
            script = f"{fid} {get_event_substring()}"
            self.widget.bind_class(class_name, sequence, f"+{script}")

        if not current_ids:
            self._bound_events.pop(key, None)

    def bind_all(self, event: str, func: Callable, *, add: bool = True, dedup: bool = False) -> str:
        """Bind a global event handler using alias-aware wrapping."""
        sequence = self._normalize(event)
        func_id = event_callback_wrapper(self.widget, func, sequence, dedup=dedup)
        script = f"{func_id} {get_event_substring()}"
        self.widget.bind_all(sequence, f"+{script}" if add else script)
        self._bound_events[f"all::{sequence}"].append(func_id)
        self._callbacks[func_id] = func
        return func_id

    def unbind_all(self, event: str, func_id: str | None = None):
        """Remove all callbacks bound globally for a specific event."""
        sequence = self._normalize(event)
        key = f"all::{sequence}"
        current_ids = self._bound_events.get(key, [])

        if func_id:
            if func_id in current_ids:
                current_ids.remove(func_id)
                self._callbacks.pop(func_id, None)
        else:
            for fid in current_ids:
                self._callbacks.pop(fid, None)
            current_ids.clear()

        self.widget.bind_all(sequence, "")
        for fid in current_ids:
            script = f"{fid} {get_event_substring()}"
            self.widget.bind_all(sequence, f"+{script}")

        if not current_ids:
            self._bound_events.pop(key, None)

    def bind_tags(self, tags: list[str] = None):
        """Get or set the bindtags for the widget."""
        if tags is None:
            return self.widget.bindtags()
        self.widget.bindtags(tags)
        return self

    def unbind(self, event: str, func_id: str | None = None):
        """Unbind a specific function or all functions from an event.

        Args:
            event: Event alias or sequence.
            func_id: Function ID to unbind. If None, all are removed.
        """
        sequence = self._normalize(event)
        current_ids = self._bound_events.get(sequence, [])

        if func_id:
            if func_id in current_ids:
                current_ids.remove(func_id)
                self._callbacks.pop(func_id, None)
        else:
            for fid in current_ids:
                self._callbacks.pop(fid, None)
            current_ids.clear()

        self.widget.tk.call("bind", str(self.widget), sequence, "")
        for fid in current_ids:
            script = f"{fid} {get_event_substring()}"
            self.widget.tk.call("bind", str(self.widget), sequence, f"+{script}")

        if not current_ids:
            self._bound_events.pop(sequence, None)

    def list_bindings(self) -> dict[str, list[str]]:
        """Return a mapping of bound events and their function IDs."""
        return dict(self._bound_events)

    def emit(self, event: str, data: dict[Any, Any] = None):
        """Programmatically trigger a virtual event.

        Args:
            event: Event alias or full virtual event string.
            data: Optional payload to pass as event data (JSON serialized).
        """
        sequence = self._normalize(event)
        if data:
            self.widget.event_generate(sequence, data=json.dumps(data))
        else:
            self.widget.event_generate(sequence)

    def process_all_events(self):
        """Enter event loop until all pending events have been processed by Tcl."""
        self.widget.update()
        return self

    def process_idle_tasks(self):
        """Enter the event loop until all idle callbacks have been called. This
        will update the display of windows but not process events caused by
        the user."""
        self.widget.update_idletasks()
        return self
