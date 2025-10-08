from tkinter import ttk
from typing import Any, Callable, Optional, Unpack

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.events import Event
from ttkbootstrap.interop.runtime.binding import Stream, Subscription
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.style.types import SemanticColor
from ttkbootstrap.types import UIEvent, Variable
from ttkbootstrap.widgets.checkbutton.events import CheckbuttonInvokeEvent
from ttkbootstrap.widgets.checkbutton.style import CheckbuttonStyleBuilder
from ttkbootstrap.widgets.checkbutton.types import CheckbuttonOptions


class Checkbutton(BaseWidget):
    """A themed checkbutton widget with support for signals and callbacks."""

    widget: ttk.Checkbutton
    _configure_methods = {
        "color": "_configure_color",
        "text": "_configure_text",
        "text_signal": "_configure_text_signal",
        "value_signal": "_configure_value_signal",
        "variable": "_configure_variable",
        "text_variable": "_configure_text_variable",
        "command": "_configure_command",
    }

    def __init__(
            self,
            text: str | Signal = None,
            value: int | str | Signal = -1,
            color: SemanticColor = 'primary',
            on_value: int | str = 1,
            off_value: int | str = 0,
            tristate_value: int | str = -1,
            command: Optional[Callable] = None,
            **kwargs: Unpack[CheckbuttonOptions]
    ):
        """
        Initialize a new Checkbutton widget.

        Args:
            text: The label text for the checkbutton.
            value: The initial value of the checkbutton.
            color: The semantic foreground color role.
            on_value: The value when checked.
            off_value: The value when unchecked.
            tristate_value: The value when in the indeterminate state.
            command: Callback fired whenever the widget is invoked.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            cursor: Mouse cursor to display when hovering over the widget.
            id: A unique identifier used to query this widget.
            parent: The parent container of this widget.
            position: The `place` container position.
            take_focus: Specifies if the widget accepts focus during keyboard traversal.
            text_variable: The tkinter text variable bound to the widget label.
            underline: The integer index (0-based) of a character to underline in the text.
            variable: The tkinter variable bound to the widget value.
            width: The width of the widget in pixels.
        """
        self._tristate_value = tristate_value
        self._style_builder = CheckbuttonStyleBuilder(color=color)
        self._value_signal_fid = None
        self._text_signal = text if isinstance(text, Signal) else Signal(text)
        self._value_signal = value if isinstance(value, Signal) else Signal(value)
        self._command = command
        self._command_sub: Optional[Subscription] = None
        self._prev_value = self._value_signal()

        parent = kwargs.pop('parent', None)

        tk_options = dict(
            textvariable=self._text_signal.var,
            variable=self._value_signal.var,
            onvalue=on_value,
            offvalue=off_value,
            **kwargs
        )
        super().__init__(ttk.Checkbutton, tk_options, parent=parent)

        # set initial state
        if value == on_value:
            self.widget.invoke()

        if value == off_value:
            self.widget.invoke()
            self.widget.invoke()

        # bind handlers
        self.widget.configure(command=self._handle_invoke)
        self._value_signal_fid = self._value_signal.subscribe(self._handle_change)

        if command:
            self._configure_command(command)

        self._value_signal_fid = self._value_signal.subscribe(self._handle_change)

    def signal(self):
        """The signal bound to the widget value"""
        return self._value_signal

    def label_signal(self):
        """The signal bound to the widget label"""
        return self._text_signal

    def is_disabled(self):
        """Return True if the checkbutton is disabled."""
        return 'disabled' in self.state()

    def is_readonly(self):
        """Return True if the checkbutton is readonly."""
        return 'readonly' in self.state()

    def is_checked(self):
        """Return True if the current value matches the on_value."""
        return 'selected' in self.widget.state()

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

    def readonly(self, value: bool):
        """Set the readonly state of the checkbutton."""
        states = []
        if self.value() == self._tristate_value:
            states.append('alternate')
        if value:
            states.extend(['disabled', 'readonly'])
        else:
            states.extend(['!disabled', '!readonly'])
        self.widget.state(states)
        return self

    def invoke(self):
        """Trigger the checkbutton as if it were toggled."""
        self.widget.invoke()
        return self

    def destroy(self):
        """Unsubscribe callbacks and destroy the widget."""
        if self._value_signal_fid:
            self._value_signal.unsubscribe(self._value_signal_fid)
            self._value_signal_fid = None
        super().destroy()

    def value(self, value: str | int = None):
        """Get or set the checkbutton value."""
        if value is None:
            return self._value_signal()
        self._value_signal.set(value)
        return self

    # ---- Event handlers ----

    def _handle_invoke(self):
        """Trigger the <<Invoke>> event when the button is clicked."""
        self.emit(Event.INVOKE, checked=self.is_checked(), value=self._value_signal(), when="tail")

    def _handle_change(self, _: Any):
        """Trigger <<Changed>> event when value signal changes"""
        value = self._value_signal()
        prev_value = self._prev_value
        on_value = self.widget.cget("onvalue")
        self.emit(Event.CHANGED, checked=value == on_value, value=value, prev_value=prev_value)
        self._prev_value = value

    def on_changed(self) -> Stream[UIEvent]:
        """Convenience alias for changed stream"""
        return self.on(Event.CHANGED)

    def on_invoke(self) -> Stream[CheckbuttonInvokeEvent]:
        """Convenience alias for invoke stream"""
        return self.on(Event.INVOKE)

    # ---- Configuration delegates -----

    def _configure_command(self, value: Callable[..., Any] = None):
        if value is None:
            return self._command
        else:
            if self._command_sub:
                self._command_sub.unlisten()
            self._command_sub = self.on_invoke().tap(lambda _: value()).then_stop()
            return self

    def _configure_color(self, value: SemanticColor = None):
        if value is None:
            return self._style_builder.options('color')
        else:
            self._style_builder.options(color=value)
            self.update_style()
            return self

    def _configure_text(self, value: str = None):
        if value is None:
            return self._text_signal()
        self._text_signal.set(value)
        return self

    def _configure_text_signal(self, value: Signal[str] = None):
        if value is None:
            return self._text_signal
        self._text_signal = value
        self.configure(textvariable=self._text_signal.var)
        return self

    def _configure_value_signal(self, value: Signal[str | int] = None):
        if value is None:
            return self._value_signal
        # change signals
        if self._value_signal_fid:
            self._value_signal.unsubscribe(self._value_signal_fid)
        self._value_signal = value
        self.configure(variable=self._value_signal.var)
        self._value_signal_fid = self._value_signal.subscribe(self._handle_change)
        self._prev_value = self._value_signal()
        return self

    def _configure_text_variable(self, value: Variable = None):
        if value is None:
            return self._text_signal
        else:
            return self._configure_text_signal(Signal.from_variable(value))

    def _configure_variable(self, value: Variable = None):
        if value is None:
            return self._value_signal
        else:
            return self._configure_value_signal(Signal.from_variable(value))


CheckButton = Checkbutton
