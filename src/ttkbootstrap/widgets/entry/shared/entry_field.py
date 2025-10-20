from abc import ABC
from typing import Any, Literal, Union

from ttkbootstrap.events import Event
from ttkbootstrap.layouts import Pack
from ttkbootstrap.style.theme import ColorTheme
from ttkbootstrap.types import Widget
from ttkbootstrap.widgets import Button
from ttkbootstrap.widgets.entry.shared.entry_mixin import EntryMixin
from ttkbootstrap.widgets.entry.shared.entry_part import EntryPart
from ttkbootstrap.widgets.label import Label


class EntryField(Pack, EntryMixin, ABC):
    """
    A composite widget combining a label, entry input (or numeric variant), optional addons, and message text.

    This widget provides a structured form input with optional label and validation message areas.
    It supports both text and number inputs, and includes methods for enabling/disabling input,
    adding prefix/suffix addons, and toggling readonly mode.
    """

    def __init__(
            self,
            *,
            value: str | int | float = None,
            label: str = None,
            message: str = None,
            show_messages: bool = True,
            required: bool = False,
            kind: str = "entry",
            **kwargs,
    ):
        """Initialize an Entry Field widget.

        Keyword Args:
            cursor: Mouse cursor when hovering.
            export_selection: Whether selection is exported to the clipboard.
            font: Font used to render text.
            foreground: Text (foreground) color.
            justify: Text alignment within the entry.
            kind: The input type, either "entry" or "manualnumeric".
            label: The label text shown above the input field.
            message: The caption or helper message shown below the input field.
            padding: Inner padding around the content.
            show: Mask character to display (e.g., '*').
            take_focus: Whether the widget can receive focus.
            text_variable: Variable bound to the entry text.
            value: The initial value of the input field.
            width: Widget width in characters.
            x_scroll_command: Callback to connect a horizontal scrollbar.
        """
        parent = kwargs.pop('parent', None)
        super().__init__(direction="vertical", parent=parent)

        # standard composite state
        self._message_text = message
        self._show_messages = show_messages
        self._theme = ColorTheme.instance()
        self._addons: dict[str, Union[Button, Label]] = {}

        # add top and bottom labels (conditionally attached)
        self._label = Label((label or '') + ('*' if required else ''), parent=self, font="label")
        self._message = Label(message, parent=self, font="caption", foreground="secondary")

        # field container & field
        self._field = Pack(parent=self, variant="field", padding=6, direction='horizontal')

        if kind in ("manualnumeric", "spinbox"):
            from ttkbootstrap.widgets.entry.shared.manual_numeric_part import ManualNumericPart
            self._entry = ManualNumericPart(value, parent=self._field, **kwargs)
        else:
            self._entry = EntryPart(value, parent=self._field, **kwargs)

        # Attach components
        label and self._label.attach(fill='x')
        self._field.attach(fill='x', expand=True)
        self._entry.attach(fill='both', expand=True)

        if self._show_messages:
            self._message.attach(fill='x')

        self._entry.on(Event.INVALID).listen(self._show_error)
        self._entry.on(Event.VALID).listen(self._clear_error)

        # Bind focus styling to the field frame
        self._entry.on(Event.FOCUS).listen(lambda _: self._field.state(["focus"]))
        self._entry.on(Event.BLUR).listen(lambda _: self._field.state(["!focus"]))

        # Add required field
        if required:
            self._entry.add_validation_rule("required")

        # Forward reference entry methods
        # ---- Event Handlers
        self.on_input = self._entry.on_input
        self.on_changed = self._entry.on_changed
        self.on_enter = self._entry.on_enter
        self.on_invalid = self._entry.on_invalid
        self.on_valid = self._entry.on_valid
        self.on_validated = self._entry.on_validated

        # ---- Entry State
        self.value = self._entry.value
        self.signal = self._entry._configure_signal

        # ---- Entry Validation
        self.add_validation_rule = self._entry.add_validation_rule
        self.add_validation_rules = self._entry.add_validation_rules
        self.validate = self._entry.validate

        # ---- Entry Behavior (curated)
        self.delete_text = self._entry.delete_text
        self.clear_selection = self._entry.clear_selection
        self.has_selection = self._entry.has_selection

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
        """Return the concrete entry widget."""
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
        kwargs.update(take_focus=False)
        if position == "right":
            instance = widget(parent=self._field, variant=variant, **kwargs)
        else:
            instance = widget(parent=self._field, variant=variant, **kwargs)
        key = name or str(instance)
        self._addons[key] = instance

        # set prefix or suffix
        options = pack_options or {}
        if position == "right":
            options.update(side=position, after=self._entry.tk_name)
            instance.attach(**options)
        else:
            options.update(side=position, before=self._entry.tk_name)
            instance.attach(**options)

        # match parent disabled state
        if 'disabled' in self.entry_widget.state():
            if hasattr(instance, 'disable'):
                instance.disable()

        # bind focus events to field frame
        instance.on(Event.FOCUS).listen(lambda _: self._field.state(['focus']))
        instance.on(Event.BLUR).listen(lambda _: self._field.state(['!focus']))
        return self

    def _show_error(self, event: Any):
        """Display a validation error message below the input field."""
        self._message.configure(text=event.data['message'])
        self._message.configure(foreground='danger')
        self._message.attach(fill='x', after=self._field)

    def _clear_error(self, _: Any):
        """Clear the validation error and reset to the original message."""
        self._message.configure(text=self._message_text)
        self._message.configure(foreground='secondary')
