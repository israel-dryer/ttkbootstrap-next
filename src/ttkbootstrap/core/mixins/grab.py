from ttkbootstrap.common.types import Widget


class GrabMixIn:
    """Mixin that provides grab control for modal behavior."""

    widget: Widget

    def acquire_grab(self):
        """Acquire a local grab, directing all events to this widget."""
        self.widget.grab_set()
        return self

    def release_grab(self):
        """Release the grab, allowing other widgets to receive events."""
        self.widget.grab_release()
        return self

    def has_grab(self) -> bool:
        """Check if this widget currently holds the grab.

        Returns:
            True if this widget has the grab, False otherwise.
        """
        return self.widget.grab_current() == str(self.widget)
