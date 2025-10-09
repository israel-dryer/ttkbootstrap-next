from typing import Unpack

from ttkbootstrap.events import Event
from ttkbootstrap.widgets import Button
from ttkbootstrap.widgets.entry.shared.entry_field import EntryField
from ttkbootstrap.widgets.entry.types import NumberEntryOptions


class NumericEntry(EntryField):
    """
    A numeric input field with optional spin buttons for incrementing and decrementing the value.

    This widget extends `EntryField` with "+" and "−" icon buttons as suffixes to allow users
    to change the value interactively. It uses an internal manual numeric entry component
    and emits "increment" and "decrement" events when the buttons are clicked.
    """

    def __init__(
            self, value="", label="", message="", show_spin_buttons=True, min_value=0.0, max_value=100.0,
            **kwargs: Unpack[NumberEntryOptions]):
        """Initialize a NumberEntry widget

        Args:
            value: The initial numeric value as a string.
            label: Optional label text displayed above the input.
            message: Optional helper or validation message shown below the input.
            show_spin_buttons: Whether to show spin buttons initially (default is True).
            min_value: Minimum allowed value (inclusive).
            max_value: Maximum allowed value (inclusive).

        Keyword Args:
            allow_blank: Whether an empty value is valid; if True, empty text commits to `None`.
            cursor: Mouse cursor when hovering.
            value_format: Intl format spec for parsing/formatting (date/number, etc.).
            export_selection: Whether selection is exported to the clipboard.
            font: Font used to render text.
            foreground: Text (foreground) color.
            increment: Step amount applied when adjusting the value.
            initial_focus: If True, the widget requests focus when shown.
            justify: Text alignment within the entry.
            kind: The input type, either "entry" or "manualnumeric".
            padding: Inner padding around the content.
            required: If True, the field must be non-empty to validate.
            show: Mask character to display (e.g., '*').
            take_focus: Whether the widget can receive focus.
            text_variable: Variable bound to the entry text.
            width: Widget width in characters.
            wrap: If True, values exceeding bounds wrap around.
            x_scroll_command: Callback to connect a horizontal scrollbar.
        """
        self._show_spin_buttons = show_spin_buttons
        # Use manual numeric stepping to keep formatting reliable while stepping
        super().__init__(
            value=value,
            label=label,
            message=message,
            kind="manualnumeric",
            min_value=min_value,
            max_value=max_value,
            **kwargs,
        )
        self.insert_addon(Button, icon="plus", name="increment", command=self.increment)
        self.insert_addon(Button, icon="dash", name="decrement", command=self.decrement)
        self.show_spin_buttons(show_spin_buttons)

    @property
    def increment_widget(self):
        return self.addons.get('increment')

    @property
    def decrement_widget(self):
        return self.addons.get('decrement')

    def increment(self):
        """Emit an 'increment' event to the numeric part."""
        self._entry.emit(Event.INCREMENT)
        return self

    def decrement(self):
        """Emit a 'decrement' event to the numeric part."""
        self._entry.emit(Event.DECREMENT)
        return self

    def show_spin_buttons(self, value: bool):
        """Show or hide the increment/decrement buttons."""
        if value:
            self.increment_widget.attach()
            self.decrement_widget.attach()
        else:
            self.increment_widget.hide()
            self.decrement_widget.hide()
        return self
