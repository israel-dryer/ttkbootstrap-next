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
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable

from ttkbootstrap.interop.runtime.commands import event_callback_wrapper
from ttkbootstrap.interop.spec.profiles import event_substring
from ttkbootstrap.events import EventType
from ttkbootstrap.types import Widget


class BindingMixin:
    """Mixin providing Tk event binding and emission helpers."""

    widget: Widget

    def __init__(self, *args, **kwargs):
        # sequence -> list of func_ids
        self.__tcl_bound_events: dict[str, list[str]] = defaultdict(list)
        # func_id -> Python callable
        self.__tcl_callbacks: dict[str, Callable[..., Any]] = {}
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
        self.widget.tk.call("bind", str(self.widget), sequence, f"+{script}" if add else script)
        self.__tcl_bound_events[sequence].append(func_id)
        self.__tcl_callbacks[func_id] = func
        return func_id

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
        self.widget.tk.call("bind", class_name, sequence, f"+{script}" if add else script)
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

    # ------------------------------------------------------------------ rebinders

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

    # ------------------------------------------------------------------ emitters

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

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _normalize(ev: EventType) -> str:
        """Normalize an Event or str to a Tk event sequence string."""
        return str(ev)
