from .base import EntryField
from ..buttons.icon_button import IconButton


class NumberEntry(EntryField):
    """
    A numeric input field with optional spin buttons for incrementing and decrementing the value.

    This widget extends `EntryField` with "+" and "−" icon buttons as suffixes to allow users
    to change the value interactively. It uses an internal `NumberSpinboxPart` for the entry component
    and emits "increment" and "decrement" events when the buttons are clicked.

    Parameters:
        parent: The parent widget.
        value: The initial numeric value as a string.
        label: Optional label text displayed above the input.
        message: Optional helper or validation message shown below the input.
        show_spin_buttons: Whether to show spin buttons initially (default is True).
        **kwargs: Additional keyword arguments passed to the underlying spinbox part.
    """

    def __init__(self, parent, value="", label="", message="", show_spin_buttons=True, **kwargs):
        self._show_spin_buttons = show_spin_buttons
        self._show_spin_buttons_pack = {}
        super().__init__(parent, value, label, message, kind="spinbox", **kwargs)
        self.insert_addon(IconButton, icon="plus", name="increment", on_click=self.increment)
        self.insert_addon(IconButton, icon="dash", name="decrement", on_click=self.decrement)
        self.show_spin_buttons(show_spin_buttons)

    @property
    def increment_widget(self):
        return self.addons.get('increment')

    @property
    def decrement_widget(self):
        return self.addons.get('decrement')

    def increment(self):
        """Emit an 'increment' event to the spinbox part."""
        self._entry.emit("increment")

    def decrement(self):
        """Emit a 'decrement' event to the spinbox part."""
        self._entry.emit("decrement")

    def show_spin_buttons(self, value: bool):
        """Show or hide the increment/decrement buttons."""
        if value:
            self.increment_widget.pack(**self._show_spin_buttons_pack.get('increment', {}))
            self.decrement_widget.pack(**self._show_spin_buttons_pack.get('decrement', {}))
        else:
            self._show_spin_buttons_pack['increment'] = self.increment_widget.pack()
            self._show_spin_buttons_pack['decrement'] = self.decrement_widget.pack()
            self.increment_widget.pack_forget()
            self.decrement_widget.pack_forget()
