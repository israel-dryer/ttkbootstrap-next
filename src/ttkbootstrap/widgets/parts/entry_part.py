from tkinter import ttk
from typing import Any, Callable, Unpack

from ttkbootstrap.core import Signal
from ttkbootstrap.core.libtypes import EntryOptions
from ttkbootstrap.core.mixins.validatable import ValidatableMixin
from ttkbootstrap.core.widget import BaseWidget
from ttkbootstrap.style.builders.entry import EntryStyleBuilder
from ttkbootstrap.utils import unsnake_kwargs


class EntryPart(BaseWidget, ValidatableMixin):
    _configure_methods = {"value", "on_enter", "on_changed", "on_change", "signal", "readonly"}

    def __init__(
            self,
            parent,
            value: str = "",
            on_change: Callable[[str], Any] = None,
            on_enter: Callable[[str], Any] = None,
            on_changed: Callable[[str], Any] = None,
            initial_focus: bool = False,
            **kwargs: Unpack[EntryOptions]
    ):
        """
        Initialize an EntryPart widget with signal binding and validation.

        Args:
            parent: The parent container.
            value: Initial value of the entry.
            on_change: Callback triggered when the signal value changes.
            on_enter: Callback triggered when Enter is pressed.
            on_changed: Callback triggered when the entry loses focus and value changed.
            initial_focus: Whether to give the entry focus after creation.
            **kwargs: Additional entry options.
        """
        self._style_builder = EntryStyleBuilder()
        self._signal = Signal(value)
        self._widget = ttk.Entry(parent, textvariable=self._signal.var, **unsnake_kwargs(kwargs))
        ValidatableMixin.__init__(self)
        super().__init__(parent)

        self._on_change = on_change
        self._on_change_fid = None
        self._on_enter = on_enter
        self._on_changed = on_changed
        self._prev_value = value

        if self._on_change:
            self.on_change(self._on_change)

        if self._on_enter:
            self.on_enter(self._on_enter)

        if self._on_changed:
            self.on_changed(self._on_changed)

        self.bind("focus", self._store_prev_value)
        self.bind("blur", self._check_if_changed)
        self._setup_validation_events()

        if initial_focus:
            self.focus()

    def _store_prev_value(self, _: Any) -> None:
        """Save the current value before focus in."""
        self._prev_value = self._signal()

    def _check_if_changed(self, _: Any) -> None:
        """Compare current value with previous and fire 'changed' event if different."""
        if self._signal() != self._prev_value:
            self.emit("changed")

    def value(self, value: str = None):
        """Get or set the entry value."""
        if value is None:
            return self._signal()
        self._signal.set(value)
        return self

    def signal(self, value: Signal[str | int] = None):
        """Get or set the signal."""
        if value is None:
            return self._signal
        self._signal = value
        self.configure(textvariable=self._signal.var)
        return self

    def on_change(self, value: Callable[[Any], Any] = None):
        """Set callback for when the signal value changes."""
        if value is None:
            return self._on_change
        if self._on_change_fid:
            self._signal.unsubscribe(self._on_change)
        self._on_change = value
        self._on_change_fid = self._signal.subscribe(self._on_change)
        return self

    def on_enter(self, value: Callable[[Any], Any] = None):
        """Set callback for when Enter is pressed."""
        if value is None:
            return self._on_enter
        self._on_enter = value
        self.bind("return", lambda _: self._on_enter(self._signal()))
        return self

    def on_changed(self, value: Callable[[str], Any] = None):
        """Set callback for when focus out causes value change."""
        if value is None:
            return self._on_changed
        self._on_changed = value
        self.bind("changed", lambda e: self._on_changed(self._signal()))
        return self

    def readonly(self, value: bool = None):
        """Get or set readonly state."""
        if value is None:
            return "readonly" in self.widget.state()
        states = ['disabled', 'readonly'] if value else ['!disabled', '!readonly']
        self.widget.state(states)
        return self

    def disable(self):
        """Disable the entry."""
        self.widget.state(['disabled'])
        return self

    def enable(self):
        """Enable the entry."""
        self.state(['!disabled', '!readonly'])
        return self

    def destroy(self) -> None:
        """Clean up subscriptions and destroy the widget."""
        if self._on_change_fid:
            self._signal.unsubscribe(self._on_change_fid)
            self._on_change_fid = None
        super().destroy()

    def get_bounding_box(self, index: int) -> tuple[int, int, int, int] | None:
        """Return bounding box of character at index."""
        return self.widget.bbox(index)

    def delete_text(self, first: int, last: int) -> None:
        """Delete text between indices."""
        self.widget.delete(first, last)

    def insert_text(self, index: int, text: str):
        """Insert text at index."""
        self.widget.insert(index, text)
        return self

    def set_cursor_index(self, index: int):
        """Set the cursor position."""
        self.widget.icursor(index)
        return self

    def get_cursor_index(self, index: str = "insert") -> int:
        """Return the character index (defaults to cursor)."""
        return self.widget.index(index)

    def start_drag_scroll(self, x: int, y: int):
        """Start drag-to-scroll behavior."""
        self.widget.scan_mark(x, y)
        return self

    def update_drag_scroll(self, x: int, y: int, gain: int = 10):
        """Continue drag-to-scroll behavior."""
        self.widget.scan_dragto(x, y, gain)
        return self

    def adjust_selection_to_index(self, index: int):
        """Adjust selection endpoint."""
        self.widget.selection_adjust(index)
        return self

    def clear_selection(self):
        """Clear text selection."""
        self.widget.selection_clear()
        return self

    def select_from_index(self, index: int):
        """Select text starting from index."""
        self.widget.selection_from(index)
        return self

    def select_to_index(self, index: int):
        """Extend selection to index."""
        self.widget.selection_to(index)
        return self

    def select_range(self, first: int, last: int):
        """Select text between two indices."""
        self.widget.selection_range(first, last)
        return self

    def has_selection(self) -> bool:
        """Return True if text is selected."""
        return self.widget.selection_present()

    def select_all(self):
        """Select all text."""
        self.widget.selection_range(0, 'end')
        return self
