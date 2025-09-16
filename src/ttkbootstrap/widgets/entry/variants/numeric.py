from typing import Unpack

from ttkbootstrap.events import Event
from ttkbootstrap.widgets import Button
from ttkbootstrap.widgets.entry.shared.entry_field import EntryField
from ttkbootstrap.widgets.entry.types import NumberEntryOptions


class NumericEntry(EntryField):
    """
    A numeric input field with optional spin buttons for incrementing and decrementing the value.

    This widget extends `EntryField` with "+" and "−" icon buttons as suffixes to allow users
    to change the value interactively. It uses an internal `NumberSpinboxPart` for the entry component
    and emits "increment" and "decrement" events when the buttons are clicked.

    Parameters:
        value: The initial numeric value as a string.
        label: Optional label text displayed above the input.
        message: Optional helper or validation message shown below the input.
        show_spin_buttons: Whether to show spin buttons initially (default is True).
        **kwargs: Additional keyword arguments passed to the underlying spinbox part.
    """

    def __init__(self, value="", label="", message="", show_spin_buttons=True, **kwargs: Unpack[NumberEntryOptions]):
        self._show_spin_buttons = show_spin_buttons
        super().__init__(value, label, message, kind="spinbox", **kwargs)
        self.insert_addon(Button, icon="plus", name="increment", on_invoke=self.increment)
        self.insert_addon(Button, icon="dash", name="decrement", on_invoke=self.decrement)
        self.show_spin_buttons(show_spin_buttons)

    @property
    def increment_widget(self):
        return self.addons.get('increment')

    @property
    def decrement_widget(self):
        return self.addons.get('decrement')

    def increment(self):
        """Emit an 'increment' event to the spinbox part."""
        self._entry.emit(Event.INCREMENT)
        return self

    def decrement(self):
        """Emit a 'decrement' event to the spinbox part."""
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
