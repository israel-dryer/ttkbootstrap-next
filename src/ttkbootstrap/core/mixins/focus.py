from tkinter import Misc
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..widget import BaseWidget


class FocusMixIn:
    """Mixin that provides focus management methods for widgets."""

    widget: Union["BaseWidget", Misc]

    def focus(self, force: bool = False):
        """Set focus to the widget.

        Args:
            force: If True, forcibly steal focus from the current widget.
        """
        if force:
            self.widget.focus_force()
        else:
            self.widget.focus_set()

    def blur(self):
        """Remove focus from the current widget."""
        self.widget.tk.call("focus", "")

    def has_focus(self) -> bool:
        """Check if this widget currently has focus.

        Returns:
            True if this widget has focus, False otherwise.
        """
        current = self.widget.tk.call("focus")
        return str(current) == str(self.widget)
