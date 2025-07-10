import json
import weakref
from collections import defaultdict
from tkinter import Misc
from typing import Any, TYPE_CHECKING, Callable, Union

from ..event_aliases import EVENT_ALIASES
from ..tkcommand import event_callback_wrapper, get_event_substring

if TYPE_CHECKING:
    from ..widget import BaseWidget


class BindingMixin:
    """Mixin that provides alias-aware event binding with substitution-based parsing.

    Uses Tcl-level event binding to support advanced substitutions (e.g., %d for data).
    Automatically wraps event handlers with converters and tracks bindings via weakrefs.
    """

    widget: Union["BaseWidget", Misc]
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

    def unbind_all(self, event: str):
        """Remove all callbacks bound to the given event sequence."""
        sequence = self._normalize(event)
        for fid in self._bound_events.get(sequence, []):
            self._callbacks.pop(fid, None)
        self._bound_events.pop(sequence, None)
        self.widget.tk.call("bind", str(self.widget), sequence, "")

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
