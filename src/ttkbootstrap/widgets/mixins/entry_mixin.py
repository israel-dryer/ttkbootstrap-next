from typing import Unpack, Union
from tkinter import ttk

# TODO add an enhanced formatting api similar to:
#  https://js.devexpress.com/Angular/Documentation/ApiReference/UI_Components/dxNumberBox/Configuration/#format


Index = Union[int, str]
EntryLike = Union[ttk.Entry, ttk.Spinbox]


class EntryMixin:
    """
    A mixin that exposes the functionality of the Entry-Like widget. Can be used with any widget
    that exposes entry behavior (i.e. SpinBox, TextEntry, etc...).
    """
    widget: EntryLike

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def enable(self):
        """Enable the widget"""
        self.widget.state(['!disabled', '!readonly'])
        return self

    def disable(self):
        """Disable the widget"""
        self.widget.state(['disabled'])
        return self

    def readonly(self, value: bool = None):
        """Get or set readonly state."""
        if value is None:
            return "readonly" in self.widget.state()
        states = ['disabled', 'readonly'] if value else ['!disabled', '!readonly']
        self.widget.state(states)
        return self

    def get_bounding_box(self, index: Index) -> tuple[int, int, int, int] | None:
        """Return bounding box of character at index."""
        return self.widget.bbox(index)

    def delete_text(self, first: Index, last: Index):
        """Delete text between indices."""
        self.widget.delete(first, last)
        return self

    def insert_text(self, index: Index, text: str):
        """Insert text at index."""
        self.widget.insert(index, text)
        return self

    def set_cursor_index(self, index: Index):
        """Set the cursor position."""
        self.widget.icursor(index)
        return self

    def get_cursor_index(self, index: Index = "insert") -> int:
        """Return the character index (defaults to cursor)."""
        return self.widget.index(index)

    def start_drag_scroll(self, x: int):
        """Start drag-to-scroll behavior."""
        self.widget.scan_mark(x)
        return self

    def update_drag_scroll(self, x: int):
        """Continue drag-to-scroll behavior."""
        self.widget.scan_dragto(x)
        return self

    def adjust_selection_to_index(self, index: Index):
        """Adjust selection endpoint."""
        self.widget.selection_adjust(index)
        return self

    def clear_selection(self):
        """Clear text selection."""
        self.widget.selection_clear()
        return self

    def select_from_index(self, index: Index):
        """Select text starting from index."""
        self.widget.selection_from(index)
        return self

    def select_to_index(self, index: Index):
        """Extend selection to index."""
        self.widget.selection_to(index)
        return self

    def select_range(self, first: Index, last: Index):
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
