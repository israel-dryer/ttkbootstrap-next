from typing import Any, Callable, Unpack

from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.validation.types import RuleType, ValidationOptions
from ttkbootstrap.validation.rules import ValidationRule
from ttkbootstrap.widgets._parts.entry_part import EntryPart
from ttkbootstrap.widgets._parts.number_spinbox_part import NumberSpinboxPart

# TODO add an enhanced formatting api similar to:
#  https://js.devexpress.com/Angular/Documentation/ApiReference/UI_Components/dxNumberBox/Configuration/#format


class EntryPartMixin:
    """
    A mixin that exposes the functionality of the EntryPart widget when composed within a
    frame that contains a `parts` property
    """
    _entry: EntryPart | NumberSpinboxPart

    def _value_or_self(self, value, func):
        if value is None: return func()
        func(value); return self

    def value(self, value: str = None):
        """Get or set the entry value."""
        return self._value_or_self(value, self._entry.value)

    def signal(self, value: Signal[str | int] = None):
        """Get or set the signal."""
        return self._value_or_self(value, self._entry.signal)

    def on_change(self, value: Callable[[Any], Any] = None):
        """Set callback for when the signal value changes."""
        return self._value_or_self(value, self._entry.on_change)

    def on_enter(self, value: Callable[[Any], Any] = None):
        """Set callback for when Enter is pressed."""
        return self._value_or_self(value, self._entry.on_enter)

    def on_changed(self, value: Callable[[str], Any] = None):
        """Set callback for when focus out causes value change."""
        return self._value_or_self(value, self._entry.on_changed)

    def readonly(self, value: bool = None):
        """Get or set readonly state."""
        return self._value_or_self(value, self._entry.readonly)

    def destroy(self) -> None:
        """Clean up subscriptions and destroy the widget."""
        return self._entry.destroy()

    def get_bounding_box(self, index: int) -> tuple[int, int, int, int] | None:
        """Return bounding box of character at index."""
        return self._value_or_self(index, self._entry.get_bounding_box)

    def delete_text(self, first: int, last: int):
        """Delete text between indices."""
        self._entry.delete_text(first, last); return self

    def insert_text(self, index: int, text: str):
        """Insert text at index."""
        self._entry.insert_text(index, text); return self

    def set_cursor_index(self, index: int):
        """Set the cursor position."""
        self._entry.set_cursor_index(index); return self

    def get_cursor_index(self, index: str = "insert") -> int:
        """Return the character index (defaults to cursor)."""
        return self._entry.get_cursor_index(index)

    def start_drag_scroll(self, x: int, y: int):
        """Start drag-to-scroll behavior."""
        self._entry.start_drag_scroll(x, y); return self

    def update_drag_scroll(self, x: int, y: int, gain: int = 10):
        """Continue drag-to-scroll behavior."""
        self._entry.update_drag_scroll(x, y, gain); return self

    def adjust_selection_to_index(self, index: int):
        """Adjust selection endpoint."""
        self._entry.adjust_selection_to_index(index); return self

    def clear_selection(self):
        """Clear text selection."""
        self._entry.clear_selection(); return self

    def select_from_index(self, index: int):
        """Select text starting from index."""
        self._entry.select_from_index(index); return self

    def select_to_index(self, index: int):
        """Extend selection to index."""
        self.select_to_index(index); return self

    def select_range(self, first: int, last: int):
        """Select text between two indices."""
        self.select_range(first, last); return self

    def has_selection(self) -> bool:
        """Return True if text is selected."""
        return self.has_selection()

    def select_all(self):
        """Select all text."""
        self._entry.select_all(); return self

    def add_validation_rule(self, rule_type: RuleType, **kwargs: Unpack[ValidationOptions]):
        self._entry.add_validation_rule(rule_type, **kwargs); return self

    def add_validation_rules(self, rules: list[ValidationRule]):
        self._entry.add_validation_rules(rules); return self
