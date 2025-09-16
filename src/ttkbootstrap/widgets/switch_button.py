from typing import Any, Callable, Optional, Unpack

from tkinter import ttk

from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.style.builders.switch_button import SwitchButtonStyleBuilder
from ttkbootstrap.style.types import SemanticColor
from ttkbootstrap.widgets.checkbutton.types import CheckbuttonOptions


class SwitchButton(BaseWidget):
    """
    A themed switch widget with support for signals and callbacks.

    Provides fluent methods for setting text, value, color, and readonly state,
    and supports binding to `Signal` objects for reactive UI behavior.
    """
    widget: ttk.Checkbutton
    _configure_methods = {
        "color": "color",
        "text_signal": "text_signal",
        "value_signal": "value_signal",
        "text": "text",
        "readonly": "readonly",
    }

    def __init__(
            self,
            text: str | Signal = None,
            value: int | str | Signal = -1,
            color: SemanticColor = "primary",
            on_value: int | str = 1,
            off_value: int | str = 0,
            on_change: Optional[Callable[[Any], Any]] = None,
            on_toggle: Optional[Callable] = None,
            **kwargs: Unpack[CheckbuttonOptions]
    ):
        """
        Initialize a new SwitchButton widget.

        Args:
            text: The label text for the checkbutton.
            color: The semantic foreground color role.
            value: The initial value of the checkbutton.
            on_value: The value when checked.
            off_value: The value when unchecked.
            on_change: Callback fired when the value signal changes.
            on_toggle: Command callback invoked on toggle.
            **kwargs: Additional keyword arguments.
        """
        self._style_builder = SwitchButtonStyleBuilder(color=color)
        self._on_change = on_change
        self._on_change_fid = None
        self._on_toggle = on_toggle
        self._text_signal = text if isinstance(text, Signal) else Signal(text or "")
        self._value_signal = value if isinstance(value, Signal) else Signal(value)

        if on_change:
            self._on_change_fid = self._value_signal.subscribe(self._on_change)

        parent = kwargs.pop("parent", None)

        tk_options = dict(
            textvariable=self._text_signal.var,
            variable=self._value_signal.var,
            onvalue=on_value,
            offvalue=off_value,
            command=self._on_toggle,
            **kwargs
        )
        super().__init__(ttk.Checkbutton, tk_options, parent=parent)

    def on_change(self, value: Callable[[Any], Any] = None):
        """Callback triggered whenever the value signal changes (even from another grouped checkbutton)"""
        if value is None:
            return self._on_change
        else:
            if self._on_change_fid:
                self._value_signal.unsubscribe(self._on_change)
            self._on_change = value
            self._on_change_fid = self._value_signal.subscribe(self._on_change)
            return self

    def color(self, value: SemanticColor = None):
        """Get or set the color role."""
        if value is None:
            return self._style_builder.options('color')
        else:
            self._style_builder.options(color=value)
            self.update_style()
            return self

    def text_signal(self, value: Signal[str] = None):
        """Get or set the checkbutton text signal."""
        if value is None:
            return self._text_signal
        self._text_signal = value
        self.configure(textvariable=self._text_signal.var)
        return self

    def value_signal(self, value: Signal[str | int] = None):
        """Get or set the checkbutton value signal."""
        if value is None:
            return self._value_signal
        self._value_signal = value
        self.configure(variable=self._value_signal.var)
        return self

    def text(self, value: str = None):
        """Get or set the checkbutton text."""
        if value is None:
            return self._text_signal()
        self._text_signal.set(value)
        return self

    def value(self, value: str | int = None):
        """Get or set the checkbutton value."""
        if value is None:
            return self._value_signal()
        self._value_signal.set(value)
        return self

    def readonly(self, value: bool = None):
        """Get or set the readonly state of the checkbutton."""
        if value is None:
            return "readonly" in self.widget.state()
        else:
            states = []
            if value:
                states.extend(['disabled', 'readonly'])
            else:
                states.extend(['!disabled', '!readonly'])
            self.widget.state(states)
            return self

    def disable(self):
        """Disable the checkbutton, preventing interaction."""
        self.widget.state(['disabled'])
        return self

    def enable(self):
        """Enable the checkbutton so it can be interacted with."""
        self.state(['!disabled', '!readonly'])

    def toggle(self):
        """Trigger the checkbutton as if it were toggled."""
        self.widget.invoke()
        return self

    def is_checked(self):
        """Return True if the current value matches the on_value."""
        return 'selected' in self.widget.state()

    def destroy(self):
        """Unsubscribe callbacks and destroy the widget."""
        if self._on_change_fid:
            self._value_signal.unsubscribe(self._on_change_fid)
            self._on_change_fid = None
        super().destroy()
