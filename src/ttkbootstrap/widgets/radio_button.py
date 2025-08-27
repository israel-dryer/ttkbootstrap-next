from typing import Any, Callable, Union, Unpack

from tkinter import ttk

from ttkbootstrap.common.types import CoreOptions
from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.style.builders.radio_button import RadioButtonStyleBuilder
from ttkbootstrap.style.types import ForegroundColor


class RadioButtonOptions(CoreOptions, total=False):
    """Optional keyword arguments accepted by the `RadioButton` widget.

    Attributes:
        cursor: Mouse cursor to display when hovering over the widget.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        underline: The integer index (0-based) of a character to underline in the text.
        width: The width of the widget in pixels.
        parent: The parent of this widget.
    """
    cursor: str
    take_focus: bool
    underline: int
    width: int


class RadioButton(BaseWidget):
    """
    A themed radio button widget with support for signal binding,
    grouped selection logic, and callback interactions.

    This widget supports reactive state updates using `Signal`, enabling
    dynamic value changes and grouped control across multiple buttons.
    """

    widget: ttk.Radiobutton
    _configure_methods = {
        "text": "text",
        "text_signal": "text_signal",
        "value": "value",
        "value_signal": "value_signal",
        "group": "group",
        "on_select": "on_select",
        "on_change": "on_change",
        "readonly": "readonly"
    }

    def __init__(
            self,
            text: str = None,
            value: str | int = 0,
            group: Union[str, Signal] = None,
            color: ForegroundColor = "primary",
            selected: bool = False,
            on_select: Callable = None,
            on_change: Callable[[Any], Any] = None,
            variant="default",
            **kwargs: Unpack[RadioButtonOptions]
    ):
        """
        Initialize a new RadioButton.

        Args:
            text: The display text for the radiobutton label.
            value: The value this radiobutton represents when selected.
            group: A signal name or Signal instance to group multiple buttons.
            color: A foreground color token for styling the label.
            selected: Whether this button should be initially selected.
            on_select: A callback triggered when the user selects the button.
            on_change: A callback triggered whenever the group value changes.
            **kwargs: Additional keyword arguments.
        """
        self._on_select = on_select
        self._on_change = on_change
        self._text_signal = Signal(text)
        self._on_change_fid = None
        self._style_builder = RadioButtonStyleBuilder(color, variant=variant)

        if group:
            self._value_signal = Signal(None, name=str(group))
        else:
            self._value_signal = Signal(value)

        if on_change:
            self._on_change_fid = self._value_signal.subscribe(self._on_change)

        parent = kwargs.pop("parent", None)

        tk_options = dict(
            value=value,
            textvariable=self._text_signal.var,
            variable=self._value_signal.var,
            command=self._on_select,
            **kwargs
        )
        super().__init__(ttk.Radiobutton, tk_options, parent=parent)

        if selected:
            self.select()

    def text(self, value: str = None):
        """Get or set the label text."""
        if value is None:
            return self._text_signal()
        self._text_signal.set(value)
        return self

    def text_signal(self, value: Signal[str] = None):
        """Get or set the signal for the label text."""
        if value is None:
            return self._text_signal
        self._text_signal = value
        self.configure(textvariable=self._text_signal.var)
        return self

    def is_selected(self):
        """Return True if the radiobutton is currently selected."""
        return 'selected' in self.widget.state()

    def value(self, value: int | str = None):
        """Get or set the current value of the radiobutton group."""
        if value is None:
            return self._value_signal()
        self._value_signal.set(value)
        return self

    def value_signal(self, value: Signal[str | int] = None):
        """Get or set the signal controlling the radiobutton group value."""
        if value is None:
            return self._value_signal
        self._value_signal = value
        self.configure(variable=self._value_signal.var)
        return self

    def on_select(self, value: Callable = None):
        """Get or set the callback triggered when this button is selected."""
        if value is None:
            return self._on_select
        self._on_select = value
        return self

    def on_change(self, value: Callable[[Any], Any] = None):
        """Get or set the callback triggered when the group value changes."""
        if value is None:
            return self._on_change
        if self._on_change_fid:
            self._value_signal.unsubscribe(self._on_change)
        self._on_change = value
        self._on_change_fid = self._value_signal.subscribe(self._on_change)
        return self

    def readonly(self, value: bool = None):
        """Get or set whether the radiobutton is readonly (disabled)."""
        if value is None:
            return "readonly" in self.widget.state()
        states = ['disabled', 'readonly'] if value else ['!disabled', '!readonly']
        self.widget.state(states)
        return self

    def disable(self):
        """Disable the radiobutton to prevent user interaction."""
        self.widget.state(['disabled'])

    def enable(self):
        """Enable the radiobutton for user interaction."""
        self.state(['!disabled', '!readonly'])
        return self

    def select(self):
        """Select this radiobutton programmatically."""
        self.widget.invoke()

    def destroy(self):
        """Unsubscribe callbacks and destroy the widget."""
        if self._on_change_fid:
            self._value_signal.unsubscribe(self._on_change_fid)
            self._on_change_fid = None
        super().destroy()
