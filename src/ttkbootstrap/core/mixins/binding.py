import weakref
from typing import TYPE_CHECKING
from ..event_aliases import EVENT_ALIASES

if TYPE_CHECKING:
    from ..widget import BaseWidget

from collections import defaultdict
from tkinter import Misc
from typing import Callable, Union


class BindingMixin:
    """Mixin that provides alias-aware event binding with weak reference tracking."""

    widget: Union["BaseWidget", Misc]
    _bound_events: dict[str, list[str]]  # event sequence → list of func IDs
    _callbacks: weakref.WeakValueDictionary[str, Callable]  # funcid → func

    def __init__(self):
        """Initialize the binding mixin with weakref tracking and alias resolution.

        Tracks function IDs for safe unbinding, supports event alias normalization,
        and prevents memory leaks by using weak references for handlers.
        """
        self._bound_events = defaultdict(list)
        self._callbacks = weakref.WeakValueDictionary()

    @staticmethod
    def _normalize(event: str) -> str:
        """Normalize an event alias to a full event sequence.

        Args:
            event: Logical or raw event string.

        Returns:
            Normalized Tkinter event sequence.
        """
        return event if "<<" in event or "<" in event else EVENT_ALIASES.get(event, f"<<{event}>>")

    def bind(self, event: str, func: Callable, *, add: bool = True) -> str:
        """Bind a callback to an event sequence.

        Args:
            event: Event alias or sequence.
            func: Callable to invoke on the event.
            add: Whether to append to existing bindings.

        Returns:
            A Tkinter-generated function ID for unbinding.
        """
        sequence = self._normalize(event)
        func_id = self.widget.bind(sequence, func, add=add)
        if func_id:
            self._bound_events[sequence].append(func_id)
            self._callbacks[func_id] = func
        return func_id

    def unbind(self, event: str, func_id: str | None = None):
        """Unbind a specific function or all functions from an event.

        Args:
            event: Event alias or sequence.
            func_id: Specific function ID to unbind. If None, all handlers are removed.
        """
        sequence = self._normalize(event)
        self.widget.unbind(sequence, func_id)
        if func_id:
            if sequence in self._bound_events:
                try:
                    self._bound_events[sequence].remove(func_id)
                    self._callbacks.pop(func_id, None)
                    if not self._bound_events[sequence]:
                        del self._bound_events[sequence]
                except ValueError:
                    pass
        else:
            for fid in self._bound_events.get(sequence, []):
                self._callbacks.pop(fid, None)
            self._bound_events.pop(sequence, None)

    def unbind_all(self, event: str):
        """Unbind all handlers associated with a specific event.

        Args:
            event: Event alias or sequence.
        """
        sequence = self._normalize(event)
        for func_id in self._bound_events.get(sequence, []):
            self.widget.unbind(sequence, func_id)
            self._callbacks.pop(func_id, None)
        self._bound_events.pop(sequence, None)

    def list_bindings(self) -> dict[str, list[str]]:
        """Return a mapping of all currently tracked event bindings.

        Returns:
            A dictionary mapping event sequences to a list of function IDs.
        """
        return dict(self._bound_events)

    def generate(self, event: EVENT_ALIASES):
        """Trigger an event sequence programmatically.

        Args:
            event: Event alias or sequence to generate.
        """
        sequence = self._normalize(event)
        self.widget.event_generate(sequence)
