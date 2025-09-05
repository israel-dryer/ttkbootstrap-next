import json
import uuid
from collections import defaultdict
from typing import Any, Callable, Dict, List

from ttkbootstrap.types import Widget
from ttkbootstrap.events import Event, EventType
from ttkbootstrap.interop.runtime.substitutions import get_event_substring
from ttkbootstrap.interop.runtime.commands import event_callback_wrapper


class BindingMixin:
    """Mixin that provides alias-aware event binding with substitution-based parsing.

    - Uses Tcl-level binding (event_callback_wrapper) for advanced % substitutions.
    - Stores strong references for callbacks to avoid GC-related invalid-command errors.
    """

    widget: Widget

    # --- Tcl-level bindings (with substitution wrapper) ---
    __tcl_bound_events: Dict[str, List[str]]  # key -> [func_id, ...]
    __tcl_callbacks: Dict[str, Callable[[Any], Any]]  # func_id -> python callable (strong ref)

    # --- Python-level alias bindings (no substitution wrapper) ---
    __py_bound_events: Dict[str, List[str]]  # sequence -> [token, ...]
    __py_callbacks: Dict[str, Callable[[Any], Any]]  # token -> python callable (strong ref)

    def __init__(self, *args, **kwargs):
        """Initialize binding state (cooperative)."""
        self.__tcl_bound_events = defaultdict(list)
        self.__tcl_callbacks = {}
        self.__py_bound_events = defaultdict(list)
        self.__py_callbacks = {}
        super().__init__(*args, **kwargs)

    # ---------------------------------------------------------------------
    # Normalization
    # ---------------------------------------------------------------------
    @staticmethod
    def _normalize(event: EventType) -> str:
        """Return the exact Tk sequence string for binding."""
        if isinstance(event, Event):
            # Expect Event.__str__ to produce the Tk sequence (e.g. "<<NotebookTabChanged>>")
            return str(event)
        if isinstance(event, str):
            # Already-formed Tk sequences
            if (event.startswith("<<") and event.endswith(">>")) or (event.startswith("<") and event.endswith(">")):
                return event
            # Logical enum name (e.g., "NotebookTabChanged")
            try:
                return str(Event(event))
            except Exception as ex:
                raise ValueError(f"Invalid event string: {event!r}") from ex
        raise TypeError(f"Unsupported event type: {type(event).__name__}")

    # ---------------------------------------------------------------------
    # Tcl-level bindings (with substitution wrapper)
    # ---------------------------------------------------------------------
    def bind(self, event: EventType, func: Callable, *, add: bool = True, dedup: bool = False) -> str:
        """Bind a callback using Tcl substitution (e.g., %d payload).

        Returns:
            func_id: Internal Tcl command name created by event_callback_wrapper.
        """
        sequence = self._normalize(event)
        func_id = event_callback_wrapper(self.widget, func, sequence, dedup=dedup)
        script = f"{func_id} {get_event_substring()}"
        self.widget.tk.call("bind", str(self.widget), sequence, f"+{script}" if add else script)
        self.__tcl_bound_events[sequence].append(func_id)
        self.__tcl_callbacks[func_id] = func  # strong ref
        return func_id

    def unbind(self, event: EventType, func_id: str | None = None) -> None:
        """Unbind a specific Tcl-level handler (by func_id) or all for that event."""
        sequence = self._normalize(event)
        ids = self._tcl_prune(sequence, func_id)
        if ids is None:
            return
        self._tcl_rebind_widget(sequence, ids)

    def bind_class(
            self, class_name: str, event: EventType, func: Callable, *, add: bool = True, dedup: bool = False) -> str:
        """Bind a callback to a widget class using Tcl substitution."""
        sequence = self._normalize(event)
        func_id = event_callback_wrapper(self.widget, func, sequence, dedup=dedup)
        script = f"{func_id} {get_event_substring()}"
        self.widget.bind_class(class_name, sequence, f"+{script}" if add else script)
        key = f"class::{class_name}::{sequence}"
        self.__tcl_bound_events[key].append(func_id)
        self.__tcl_callbacks[func_id] = func
        return func_id

    def unbind_class(self, class_name: str, event: EventType, func_id: str | None = None) -> None:
        """Unbind class-level Tcl bindings (by func_id or all)."""
        sequence = self._normalize(event)
        key = f"class::{class_name}::{sequence}"
        ids = self._tcl_prune(key, func_id)
        if ids is None:
            return
        self._tcl_rebind_class(class_name, sequence, ids)

    def bind_all(self, event: EventType, func: Callable, *, add: bool = True, dedup: bool = False) -> str:
        """Bind a global (application-wide) Tcl-level handler."""
        sequence = self._normalize(event)
        func_id = event_callback_wrapper(self.widget, func, sequence, dedup=dedup)
        script = f"{func_id} {get_event_substring()}"
        self.widget.bind_all(sequence, f"+{script}" if add else script)
        key = f"all::{sequence}"
        self.__tcl_bound_events[key].append(func_id)
        self.__tcl_callbacks[func_id] = func
        return func_id

    def unbind_all(self, event: EventType, func_id: str | None = None) -> None:
        """Unbind global Tcl-level handlers (by func_id or all)."""
        sequence = self._normalize(event)
        key = f"all::{sequence}"
        ids = self._tcl_prune(key, func_id)
        if ids is None:
            return
        self._tcl_rebind_all(sequence, ids)

    # ---------------------------------------------------------------------
    # Python-level convenience bindings (no substitution wrapper)
    # ---------------------------------------------------------------------
    def bind_alias(self, sequence: str, callback: Callable[[Any], Any], *, add: bool = True) -> str:
        """Bind a Python callback directly via Tk, returning a token for later unbind."""
        seq = self._normalize(sequence)
        token = uuid.uuid4().hex
        self.__py_callbacks[token] = callback
        self.widget.bind(seq, callback, add="+" if add else None)
        self.__py_bound_events[seq].append(token)
        return token

    def unbind_alias(self, sequence: str, token: str) -> None:
        """Unbind a previously-bound alias callback (by token) and keep others intact."""
        seq = self._normalize(sequence)
        tokens = self._py_prune(seq, token)
        if tokens is None:
            return
        self._py_rebind(seq, tokens)

    def unbind_sequence(self, sequence: str) -> None:
        """Remove all alias callbacks bound to a specific sequence."""
        seq = self._normalize(sequence)
        tokens = self._py_prune(seq, None)
        if tokens is None:
            return
        self._py_rebind(seq, tokens)  # tokens [] → remains cleared

    def unbind_all_aliases(self) -> None:
        """Remove all alias bindings (call on widget destroy)."""
        for seq in list(self.__py_bound_events.keys()):
            self.widget.unbind(seq)
        self.__py_bound_events.clear()
        self.__py_callbacks.clear()

    # ---------------------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------------------
    def bind_tags(self, tags: list[str] | None = None):
        """Get or set the bindtags for the widget."""
        if tags is None:
            return self.widget.bindtags()
        self.widget.bindtags(tags)
        return self

    def list_bindings(self) -> dict[str, list[str]]:
        """Return a snapshot mapping of Tcl-level bindings and their func_ids."""
        return dict(self.__tcl_bound_events)

    def emit(self, event: EventType, data: dict[Any, Any] | None = None, **kwargs):
        """Programmatically trigger a (virtual) event; payload serialized to event.data."""
        sequence = self._normalize(event)
        if data:
            self.widget.event_generate(sequence, data=json.dumps(data), **kwargs)
        else:
            self.widget.event_generate(sequence, **kwargs)
        return self

    def process_all_events(self):
        """Process all pending events."""
        self.widget.update()
        return self

    def process_idle_tasks(self):
        """Process all idle callbacks (no user events)."""
        self.widget.update_idletasks()
        return self

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _tcl_prune(self, key: str, func_id: str | None) -> List[str] | None:
        """Remove one/all tcl func_ids for the key (sequence/class/all) and cleanup refs.
        Returns surviving list (possibly empty) or None if key not present.
        """
        ids = self.__tcl_bound_events.get(key)
        if ids is None:
            return None

        if func_id is None:
            for fid in ids:
                self.__tcl_callbacks.pop(fid, None)
            ids.clear()
        else:
            try:
                ids.remove(func_id)
            except ValueError:
                pass
            else:
                self.__tcl_callbacks.pop(func_id, None)

        if not ids:
            self.__tcl_bound_events.pop(key, None)
            return []
        return ids

    def _tcl_rebind_widget(self, sequence: str, ids: List[str]) -> None:
        self.widget.tk.call("bind", str(self.widget), sequence, "")
        for fid in ids:
            script = f"{fid} {get_event_substring()}"
            self.widget.tk.call("bind", str(self.widget), sequence, f"+{script}")

    def _tcl_rebind_class(self, class_name: str, sequence: str, ids: List[str]) -> None:
        self.widget.bind_class(class_name, sequence, "")
        for fid in ids:
            script = f"{fid} {get_event_substring()}"
            self.widget.bind_class(class_name, sequence, f"+{script}")

    def _tcl_rebind_all(self, sequence: str, ids: List[str]) -> None:
        self.widget.bind_all(sequence, "")
        for fid in ids:
            script = f"{fid} {get_event_substring()}"
            self.widget.bind_all(sequence, f"+{script}")

    def _py_prune(self, sequence: str, token: str | None) -> List[str] | None:
        """Remove one/all python tokens for a sequence and cleanup refs.
        Returns surviving tokens (possibly empty) or None if no entry.
        """
        tokens = self.__py_bound_events.get(sequence)
        if tokens is None:
            return None

        if token is None:
            for t in tokens:
                self.__py_callbacks.pop(t, None)
            tokens.clear()
        else:
            try:
                tokens.remove(token)
            except ValueError:
                pass
            else:
                self.__py_callbacks.pop(token, None)

        if not tokens:
            self.__py_bound_events.pop(sequence, None)
            return []
        return tokens

    def _py_rebind(self, sequence: str, tokens: List[str]) -> None:
        self.widget.unbind(sequence)
        for t in tokens:
            cb = self.__py_callbacks.get(t)
            if cb is not None:
                self.widget.bind(sequence, cb, add="+")
