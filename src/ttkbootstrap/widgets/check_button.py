from typing import Any, Callable, Optional, Unpack

from tkinter import ttk
from ttkbootstrap.core import Signal
from ttkbootstrap.core.libtypes import CheckButtonOptions
from ttkbootstrap.core.widget import BaseWidget
from ttkbootstrap.style.builders.check_button import CheckButtonStyleBuilder
from ttkbootstrap.style.tokens import SemanticColor
from ttkbootstrap.utils import unsnake_kwargs


class CheckButton(BaseWidget):
    """
    A themed checkbutton widget with support for signals and callbacks.

    Provides fluent methods for setting text, value, color, and readonly state,
    and supports binding to `Signal` objects for reactive UI behavior.
    """

    _configure_methods = {"color", "text_signal", "value_signal", "text", "readonly", "on_change", "on_toggle"}

    def __init__(
            self,
            parent,
            text: str,
            color: SemanticColor = None,
            value: int | str = -1,
            on_value: int | str = 1,
            off_value: int | str = 0,
            tristate_value: int | str = -1,
            on_change: Optional[Callable[[Any], Any]] = None,
            on_toggle: Optional[Callable] = None,
            **kwargs: Unpack[CheckButtonOptions]
    ):
        """
        Initialize a new CheckButton widget.

        Args:
            parent: The parent widget.
            text: The label text for the checkbutton.
            color: The semantic foreground color role.
            value: The initial value of the checkbutton.
            on_value: The value when checked.
            off_value: The value when unchecked.
            tristate_value: The value when in the indeterminate state.
            on_change: Callback fired when the value signal changes.
            on_toggle: Command callback invoked on toggle.
            **kwargs: Additional keyword arguments passed to `ttk.Checkbutton`.
        """
        self._tristate_value = tristate_value
        self._style_builder = CheckButtonStyleBuilder(color)
        self._on_change = on_change
        self._on_change_fid = None
        self._on_toggle = on_toggle
        self._text_signal = Signal(text)
        self._value_signal = Signal(value)

        if on_change:
            self._on_change_fid = self._value_signal.subscribe(self._on_change)

        self._widget = ttk.Checkbutton(
            parent,
            textvariable=self._text_signal.var,
            onvalue=on_value,
            offvalue=off_value,
            command=self._internal_toggle,
            **unsnake_kwargs(kwargs)
        )
        super().__init__(parent)

        # set initial state
        if value == on_value:
            self.widget.invoke()
        if value == off_value:
            self.widget.invoke()
            self.widget.invoke()

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
            return self._style_builder.color()
        else:
            self._style_builder.color(value)
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
            if self.value() == self._tristate_value:
                states.append('alternate')
            if value:
                states.extend(['disabled', 'readonly'])
            else:
                states.extend(['!disabled', '!readonly'])
            self.widget.state(states)
            return self

    def disable(self):
        """Disable the checkbutton, preventing interaction."""
        if self.value() == self._tristate_value:
            self.widget.state(['disabled', 'alternate'])
        else:
            self.widget.state(['disabled'])
        return self

    def enable(self):
        """Enable the checkbutton so it can be interacted with."""
        if self.value() == self._tristate_value:
            self.state(['!disabled', '!readonly', 'alternate'])
        else:
            self.state(['!disabled', '!readonly'])
        return self

    def _internal_toggle(self):
        """Handle toggle command from checkbutton widget"""
        on_value = self.configure('on_value')
        off_value = self.configure('off_value')

        if self._on_toggle:
            self._on_toggle()
        self.value(on_value if self.is_checked() else off_value)

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
