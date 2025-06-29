from tkinter import Misc
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..widget import BaseWidget


class GrabMixIn:
    """Mixin that provides grab control for modal behavior."""

    widget: Union["BaseWidget", Misc]

    def acquire_grab(self):
        """Acquire a local grab, directing all events to this widget."""
        self.widget.grab_set()

    def release_grab(self):
        """Release the grab, allowing other widgets to receive events."""
        self.widget.grab_release()

    def has_grab(self) -> bool:
        """Check if this widget currently holds the grab.

        Returns:
            True if this widget has the grab, False otherwise.
        """
        return self.widget.grab_current() == str(self.widget)
