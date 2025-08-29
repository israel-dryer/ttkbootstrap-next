from abc import ABC
from typing import Any, Literal, Union

from ttkbootstrap.types import Widget
from ttkbootstrap.events import Event
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import Button
from ttkbootstrap.widgets.parts.entry_part import EntryPart
from ttkbootstrap.widgets.parts.number_spinner_part import NumberSpinnerPart
from ttkbootstrap.widgets.label import Label
from ttkbootstrap.widgets.mixins.entry_mixin import EntryMixin
from ttkbootstrap.style.theme import ColorTheme


class EntryField(Pack, EntryMixin, ABC):
    """
    A composite widget combining a label, entry/spinbox input, optional addons, and message text.

    This widget provides a structured form input with optional label and validation message areas.
    It supports both text and number inputs, and includes methods for enabling/disabling input,
    adding prefix/suffix addons, and toggling readonly mode.

    Args:
        parent: The parent container for the EntryField.
        value: The initial value of the input field.
        label: The label text shown above the input field.
        message: The caption or helper message shown below the input field.
        kind: The input type, either "entry" (default) or "spinbox".
        **kwargs: Additional keyword arguments passed to the input widget.
    """

    def __init__(
            self,
            value: str | int | float = None,
            label: str = None,
            message: str = None,
            kind: str = "entry",
            enable_validation: bool = False,
            **kwargs,
    ):
        super().__init__(direction="vertical")

        # standard composite state
        self._message_text = message
        self._enable_validation = enable_validation
        self._theme = ColorTheme.instance()
        self._addons: dict[str, Union[Button, Label]] = {}

        # add top and bottom labels (conditionally attached)
        self._label = Label(label, parent=self, font="label").layout(fill='x')
        self._message = Label(message, parent=self, font="caption", foreground="secondary").layout(fill='x')

        # field container & field
        self._field = Pack(parent=self, variant="field", padding=6, direction='horizontal')
        self._field.layout(fill='x', expand=True)

        if kind == "spinbox":
            self._entry = NumberSpinnerPart(value, parent=self._field, **kwargs).layout(fill='both', expand=True)
        else:
            self._entry = EntryPart(value, parent=self._field, **kwargs).layout(fill='both', expand=True)

        # Attach components
        label and self._label.attach()
        self._field.attach()
        self._entry.attach()
        (self._enable_validation or self._message_text) and self._message.attach()

        if self._enable_validation:
            self._entry.bind(Event.INVALID, self._show_error)
            self._entry.bind(Event.VALID, self._clear_error)

        # Bind focus styling to the field frame
        self._entry.bind(Event.FOCUS, lambda e: self._field.state(["focus"]))
        self._entry.bind(Event.BLUR, lambda e: self._field.state(["!focus"]))

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
        """
        Get or set readonly state of the input.

        Args:
            value: If None, returns current readonly state. Otherwise, sets the state.

        Returns:
            The current readonly state or self (for chaining).
        """
        if value == False:
            self._field.state(['disabled'])
        elif value:
            self._field.state(['!disabled'])
        if value is None:
            return self._entry.readonly()
        else:
            self._entry.readonly(value)
            return self

    def insert_addon(
            self,
            widget: Widget,
            position: Literal['left', 'right'] = "right",
            name=None,
            pack_options: dict[str, Any] = None,
            **kwargs
    ):
        """
        Insert a widget as an addon before or after the input.

        Args:
            widget: A callable widget class (e.g., IconButton).
            position: The position of the widget relative to the input ("left" or "right").
            name: Optional name to reference the addon.
            pack_options: Optional dictionary of pack options.
            **kwargs: Additional arguments passed to the widget constructor.
        """
        variant = "suffix" if position == "right" else "prefix"
        if position == "right":
            instance = widget(parent=self._field, variant=variant, **kwargs)
        else:
            instance = widget(parent=self._field, variant=variant, **kwargs)
        key = name or str(instance)
        self._addons[key] = instance

        # set prefix or suffix
        options = pack_options or {}
        if position == "right":
            options.update(side=position, after=self._entry)
            instance.attach(**options)
        else:
            options.update(side=position, before=self._entry)
            instance.attach(**options)

        # match parent disabled state
        if 'disabled' in self.entry_widget.state():
            if hasattr(instance, 'disable'):
                instance.disable()

        # bind focus events to field frame
        instance.bind(Event.FOCUS, lambda e: self._field.state(['focus']))
        instance.bind(Event.BLUR, lambda e: self._field.state(['!focus']))
        return self

    def _show_error(self, event: Any):
        """Display a validation error message below the input field."""
        self._message.text(event.data['message'])
        self._message.configure(foreground='danger')
        self._message.attach(fill='x', after=self._field)

    def _clear_error(self, _: Any):
        """Clear the validation error and reset to the original message."""
        self._message.text(self._message_text)
        self._message.configure(foreground='secondary')
