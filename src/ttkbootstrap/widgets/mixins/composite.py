from ttkbootstrap.core.widget import BaseWidget


class CompositeWidgetMixin:
    """Mixin that allows composite widgets to synchronize interactive states
    (e.g., hover, pressed) between a container and its child widgets."""

    def __init__(self):
        self._composite_widgets: "BaseWidget" = []

    def register_composite_widgets(self, widgets: list["BaseWidget"]):
        """Register child widgets that should sync states with the container.

        Args:
            widgets: A list of Widget instances.
        """
        self._composite_widgets = widgets

        for widget in widgets + [self]:
            widget.bind("enter", self._on_enter)
            widget.bind("leave", self._on_leave)
            widget.bind("mouse_down", self._on_press)
            widget.bind("mouse_up", self._on_release)

    def _apply_state(self, state: str, enable: bool):
        """Apply or remove a state to all registered widgets."""
        for widget in self._composite_widgets + [self]:
            if hasattr(widget, "state"):
                if enable:
                    widget.state([state])
                else:
                    widget.state([f"!{state}"])

    def _on_enter(self, event=None):
        self._apply_state("hover", True)

    def _on_leave(self, event=None):
        self._apply_state("hover", False)

    def _on_press(self, event=None):
        self._apply_state("pressed", True)

    def _on_release(self, event=None):
        self._apply_state("pressed", False)
