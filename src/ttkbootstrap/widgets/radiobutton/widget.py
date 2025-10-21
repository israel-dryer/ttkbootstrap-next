from enum import Enum
from tkinter import ttk
from typing import Any, Callable, Optional, Union, Unpack

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.events import Event
from ttkbootstrap.interop.runtime.binding import Stream, Subscription
from ttkbootstrap.interop.runtime.configure import configure_delegate
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.style.types import ForegroundColor, SemanticColor
from ttkbootstrap.types import Variable
from ttkbootstrap.widgets.radiobutton.events import RadiobuttonDeselectedEvent, RadiobuttonSelectedEvent
from ttkbootstrap.widgets.radiobutton.style import RadiobuttonStyleBuilder
from ttkbootstrap.widgets.radiobutton.types import RadiobuttonOptions


class Radiobutton(BaseWidget):
    """A themed radio button widget with support for signal binding,
    grouped selection logic, and callback interactions.
    """

    widget: ttk.Radiobutton

    def __init__(
            self,
            text: str = "",
            value: str | int = 0,
            group: Union[str, Signal] = None,
            *,
            color: ForegroundColor = "primary",
            selected: bool = False,
            command: Optional[Callable] = None,
            variant="default",
            **kwargs: Unpack[RadiobuttonOptions]
    ):
        """
        Initialize a new RadioButton.

        Args:
            text: The display text for the radiobutton label.
            value: The value this radiobutton represents when selected.
            group: A signal name or Signal instance to group multiple buttons.

        Keyword Args:
            color: A foreground color token for styling the label.
            command: Callback fired when the button is invoked.
            cursor: Mouse cursor to display when hovering over the widget.
            id: A unique identifier used to query this widget.
            parent: The parent container of this widget.
            selected: Whether this button should be initially selected.
            take_focus: Specifies if the widget accepts focus during keyboard traversal.
            text_variable: The tkinter text variable bound to the widget label.
            underline: The integer index (0-based) of a character to underline in the text.
            variable: The tkinter variable bound to the widget value.
            width: The width of the widget in pixels.
        """
        self._style_builder = RadiobuttonStyleBuilder(color=color, variant=variant)
        self._text_signal = Signal(text)
        self._value_signal = None
        self._command = command
        self._command_sub: Optional[Subscription] = None
        self._group = group

        if isinstance(group, Signal):
            self._value_signal = group
        elif isinstance(group, str) and group:
            # seed the named signal with `value` to establish type (str/int)
            self._value_signal = Signal(self._coerce_to_signal_type(value), name=group)
        else:
            self._value_signal = Signal(self._coerce_to_signal_type(value))
        self._prev_value = self._value_signal()

        parent = kwargs.pop("parent", None)

        tk_options = dict(
            value=value,
            textvariable=self._text_signal.var,
            variable=self._value_signal.var,
            **kwargs
        )
        super().__init__(ttk.Radiobutton, tk_options, parent=parent)

        # set initial value
        if selected:
            self.select()

        # Add event handlers
        self.widget.configure(command=self._handle_invoke)

        if command:
            self._configure_command(command)

        self._value_signal_fid = self._value_signal.subscribe(self._handle_change)

    def signal(self):
        """The signal bound to the widget value"""
        return self._value_signal

    def text_signal(self):
        """The signal bound to the widget label"""
        return self._text_signal

    def is_selected(self):
        """Return True if the radiobutton is currently selected."""
        return 'selected' in self.widget.state()

    def is_readonly(self):
        """Return True if the radiobutton is readonly."""
        return 'readonly' in self.state()

    def readonly(self, value: bool):
        """Get or set whether the radiobutton is readonly (disabled)."""
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

    def invoke(self):
        """Calls the function associated with the on_invoke handler"""
        self.widget.invoke()
        return self

    def select(self):
        """Select this radiobutton"""
        value = self.widget.cget('value')
        self._value_signal.set(self._coerce_to_signal_type(value))
        return self

    def destroy(self):
        """Unsubscribe callbacks and destroy the widget."""
        if self._signal_fid:
            self._value_signal.unsubscribe(self._signal_fid)
            self._signal_fid = None
        super().destroy()

    def value(self, value: int | str = None):
        """Get or set the current value of the radiobutton group."""
        if value is None:
            return self._value_signal()
        self._value_signal.set(value)
        return self

    # ----- Event handlers -----

    def on_selected(self) -> Stream[RadiobuttonSelectedEvent]:
        """Convenience alias for the selected stream"""
        return self.on(Event.SELECTED)

    def on_deselected(self) -> Stream[RadiobuttonDeselectedEvent]:
        """Convenience alias for the deselected stream"""
        return self.on(Event.RADIO_DESELECTED)

    def on_invoke(self):
        """Convenience alias for the invoke stream"""
        return self.on(Event.INVOKE)

    def _handle_invoke(self):
        """Trigger <<Invoke>> when the button is activated"""
        self.emit(Event.INVOKE, selected=self.is_selected(), value=self._value_signal(), when="tail")

    def _handle_change(self, _: Any):
        """Trigger <<RadioSelected>> / <<RadioDeselected>> on group value changes."""
        value = self._value_signal()
        prev_value = self._prev_value
        on_value = self._coerce_to_signal_type(self.widget.cget("value"))

        if value == on_value and prev_value != on_value:
            self.emit(Event.RADIO_SELECTED, selected=True, value=value, prev_value=prev_value, when="tail")
        elif prev_value == on_value and value != on_value:
            self.emit(Event.RADIO_DESELECTED, selected=False, value=value, prev_value=prev_value, when="tail")

        self._prev_value = value

    # ----- Configuration delegates -----

    @configure_delegate("command")
    def _configure_command(self, value: Callable[..., Any] = None):
        if value is None:
            return self._command
        else:
            if self._command_sub:
                self._command_sub.unlisten()
            self._command_sub = self.on_invoke().tap(lambda _: value()).then_stop()
            return self

    @configure_delegate("color")
    def _configure_color(self, value: SemanticColor = None):
        if value is None:
            return self._style_builder.options('color')
        else:
            self._style_builder.options(color=value)
            self.update_style()
            return self

    @configure_delegate("text")
    def _configure_text(self, value: str = None):
        if value is None:
            return self._text_signal()
        self._text_signal.set(value)
        return self

    @configure_delegate("text_signal")
    def _configure_text_signal(self, value: Signal[str] = None):
        if value is None:
            return self._text_signal
        self._text_signal = value
        self.configure(textvariable=self._text_signal.var)
        return self

    @configure_delegate("value_signal")
    def _configure_value_signal(self, value: Signal[str | int] = None):
        if value is None:
            return self._value_signal
        # change signals
        if self._signal_fid:
            self._value_signal.unsubscribe(self._signal_fid)
        self._value_signal = value
        self.configure(variable=self._value_signal.var)
        self._signal_fid = self._value_signal.subscribe(self._handle_change)
        self._prev_value = self._value_signal()
        return self

    @configure_delegate("text_variable")
    @configure_delegate("textvariable")
    def _configure_text_variable(self, value: Variable = None):
        if value is None:
            return self._text_signal
        else:
            return self._configure_text_signal(Signal.from_variable(value))

    @configure_delegate("variable")
    def _configure_variable(self, value: Variable = None):
        if value is None:
            return self._value_signal
        else:
            return self._configure_value_signal(Signal.from_variable(value))

    # ----- Helpers -----

    def _coerce_to_signal_type(self, v):
        # Align the radiobutton's 'value' with the group's Signal[T] type
        t = getattr(self._value_signal, "_type", None)

        # Fast paths
        if t is int:   return int(v)
        if t is float: return float(v)
        if t is str:   return str(v)

        try:
            # Enum: try by value, then by name
            if isinstance(t, type) and issubclass(t, Enum):
                try:
                    return t(v)
                except ValueError:
                    return t[str(v)]
            # Generic callable (skip if not callable, e.g. typing.Union)
            return t(v) if callable(t) else v
        except (ValueError, TypeError, KeyError):
            return v


RadioButton = Radiobutton
