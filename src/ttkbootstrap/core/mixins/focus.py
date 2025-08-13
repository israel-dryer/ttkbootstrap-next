from tkinter import Widget


class FocusMixIn:
    """Mixin that provides focus management methods for widgets."""

    widget: Widget

    def focus(self, force: bool = False):
        """Set focus to the widget.

        Args:
            force: If True, forcibly steal focus from the current widget.
        """
        if force:
            self.widget.focus_force()
        else:
            self.widget.focus_set()
        return self

    def blur(self):
        """Remove focus from the current widget."""
        self.widget.tk.call("focus", "")
        return self

    def has_focus(self) -> bool:
        """Check if this widget currently has focus.

        Returns:
            True if this widget has focus, False otherwise.
        """
        current = self.widget.tk.call("focus")
        return str(current) == str(self.widget)
