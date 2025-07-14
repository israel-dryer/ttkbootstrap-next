from abc import ABC
from typing import Literal, Union

from . import Button, IconButton
from .frame import Frame
from .label import Label
from .parts import EntryPart, NumberSpinboxPart
from .parts.mixins.entry_part_mixin import EntryPartMixin
from ..style.theme import ColorTheme


class EntryField(Frame, EntryPartMixin, ABC):
    """
    A composite widget combining a label, entry/spinbox input, optional addons, and message text.

    This widget provides a structured form input with optional label and validation message areas.
    It supports both text and number inputs, and includes methods for enabling/disabling input,
    adding prefix/suffix addons, and toggling readonly mode.

    Parameters:
        parent: The parent container for the EntryField.
        value (str | int | float, optional): The initial value of the input field.
        label (str, optional): The label text shown above the input field.
        message (str, optional): The caption or helper message shown below the input field.
        kind (str, optional): The input type, either "entry" (default) or "spinbox".
        **kwargs: Additional keyword arguments passed to the input widget.

    Example:
        field = EntryField(parent, label="Name", message="Enter your full name.")
        field.insert_addon(IconButton, side='right', icon='search')
    """

    def __init__(
            self, parent,
            value: str | int | float = None,
            label: str = None,
            message: str = None,
            kind="entry",
            **kwargs):
        super().__init__(parent)

        # add default parts
        self._label = Label(self, label, font="label", anchor="w")
        self._field = Frame(self, variant="field", padding=5)
        self._message = Label(self, message, font="caption", foreground='secondary')
        self._message_text = message
        self._theme = ColorTheme.instance()

        self._addons: dict[str, Union[Button, IconButton, Label]] = dict()

        if kind == "spinbox":
            self._entry = NumberSpinboxPart(self._field, value=value, **kwargs)
        else:
            self._entry = EntryPart(self._field, value=value, **kwargs)

        self._field.pack(fill='x', expand=True)
        self._entry.pack(side='left', fill='both', expand=True)

        if label:
            self._label.pack(fill='x', before=self._field)

        self._message.pack(fill='x', after=self._field)

        # bind focus events to field frame
        self._entry.bind("focus", lambda e: self._field.state(['focus']))
        self._entry.bind('blur', lambda e: self._field.state(['!focus']))

        # bind validation message
        self._entry.bind("invalid", self._show_error)
        self._entry.bind("valid", self._clear_error)

    @property
    def addons(self):
        """Return the dictionary of inserted addon widgets."""
        return self._addons

    @property
    def label_widget(self):
        """Return the label widget."""
        return self._label

    @property
    def entry_widget(self):
        """Return the entry or spinbox widget."""
        return self._entry

    @property
    def message_widget(self):
        """Return the message label widget."""
        return self._message

    def disable(self):
        """Disable the input and all addon widgets."""
        self._entry.disable()
        self._field.state(['disabled'])
        for item in self._addons.values():
            if hasattr(item, 'disable'):
                item.disable()
        return self

    def enable(self):
        """Enable the input and all addon widgets."""
        self._entry.enable()
        self._field.state(['!disabled'])
        for item in self._addons.values():
            if hasattr(item, 'enable'):
                item.enable()
        return self

    def readonly(self, value: bool = None):
        """Get or set readonly state of the input."""
        if value == False:
            self._field.state(['disabled'])
        elif value:
            self._field.state(['!disabled'])
        if value is None:
            return self._entry.readonly()
        else:
            self._entry.readonly(value)
            return self

    def insert_addon(self, widget, side: Literal['left', 'right'] = "right", name=None, **kwargs):
        """Insert a widget as an addon to the left or right of the input."""
        variant = "suffix" if side == "right" else "prefix"
        instance = widget(self._field, variant=variant, **kwargs)
        key = name or str(instance)
        self._addons[key] = instance
        if side == "right":
            instance.pack(side=side, after=self._entry)
        else:
            instance.pack(side=side, before=self._entry)

        # match parent disabled state
        if 'disabled' in self.entry_widget.state():
            if hasattr(instance, 'disable'):
                instance.disable()

        # bind focus events to field frame
        instance.bind("focus", lambda e: self._field.state(['focus']))
        instance.bind('blur', lambda e: self._field.state(['!focus']))

    def _show_error(self, event: any):
        """Display a validation error message below the input field."""
        self._message.text(event.data['message'])
        self._message.configure(foreground='danger')
        self._message.pack(fill='x', after=self._field)

    def _clear_error(self, _: any):
        """Clear the validation error and reset to the original message."""
        self._message.text(self._message_text)
        self._message.configure(foreground='secondary')
