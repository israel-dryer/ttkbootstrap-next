from __future__ import annotations
from typing import Self

from ttkbootstrap_next.types import Widget


class FocusMixin:
    """Mixin that provides focus management methods for widgets."""

    widget: Widget

    def __init__(self, *args, **kwargs):
        """Cooperative init to play nice with multiple inheritance."""
        super().__init__(*args, **kwargs)

    def focus(self, force: bool = False) -> Self:
        """Set focus to this widget.

        Args:
            force: If True, forcibly steal focus from the current widget (even if not viewable).
        """
        if force:
            self.widget.focus_force()
        else:
            self.widget.focus_set()
        return self

    def blur(self) -> Self:
        """Remove focus from the current widget (clears focus on the display)."""
        # Equivalent to Tk: focus ""
        self.widget.tk.call("focus", "")
        return self

    def has_focus(self) -> bool:
        """Return True if this widget currently has keyboard focus."""
        current = self.widget.tk.call("focus")
        return bool(current) and str(current) == str(self.widget)
