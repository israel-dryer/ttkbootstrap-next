from tkinter import ttk
from typing import Any, Optional, Self, Unpack

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.events import Event
from ttkbootstrap.interop.runtime.binding import Stream
from ttkbootstrap.interop.runtime.utils import coerce_handler_args
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.style.builders.check_button import CheckButtonStyleBuilder
from ttkbootstrap.style.types import SemanticColor
from ttkbootstrap.types import AltEventHandler, CoreOptions, EventHandler


class CheckButtonOptions(CoreOptions, total=False):
    """Optional keyword arguments accepted by the `CheckButton` widget.

    Attributes:
        cursor: Mouse cursor to display when hovering over the widget.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        underline: The integer index (0-based) of a character to underline in the text.
        width: The width of the widget in pixels.
    """
    cursor: str
    take_focus: bool
    underline: int
    width: int


class CheckButton(BaseWidget):
    """
    A themed checkbutton widget with support for signals and callbacks.

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
            color: SemanticColor = 'primary',
            on_value: int | str = 1,
            off_value: int | str = 0,
            tristate_value: int | str = -1,
            on_changed: Optional[EventHandler] = None,
            on_invoke: Optional[AltEventHandler] = None,
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
            on_changed: Callback fired when the value signal changes.
            on_invoke: Callback fired when the button is invoked.
            **kwargs: Additional keyword arguments.
        """
        self._tristate_value = tristate_value
        self._style_builder = CheckButtonStyleBuilder(color=color)
        self._on_changed = on_changed
        self._on_changed_fid = None
        self._text_signal = text if isinstance(text, Signal) else Signal(text)
        self._value_signal = value if isinstance(value, Signal) else Signal(value)
        self._prev_value = self._value_signal()

        parent = kwargs.pop('parent', None)

        tk_options = dict(
            textvariable=self._text_signal.var,
            variable=self._value_signal.var,
            onvalue=on_value,
            offvalue=off_value,
            command=self._handle_invoke,
            **kwargs
        )
        super().__init__(ttk.Checkbutton, tk_options, parent=parent)

        # set initial state
        if value == on_value:
            self.widget.invoke()

        if value == off_value:
            self.widget.invoke()
            self.widget.invoke()

        # bind initial handlers
        if on_changed:
            self.on_changed(on_changed)

        if on_invoke:
            self.on_invoke(on_invoke)

        self._on_changed_fid = self._value_signal.subscribe(self._handle_change)

    def _handle_invoke(self):
        """Trigger the <<Invoke>> event when the button is clicked."""
        self.emit(Event.INVOKE, checked=self.is_checked(), value=self._value_signal())

    def _handle_change(self, _: Any):
        """Trigger <<Changed>> event when value signal changes"""
        value = self._value_signal()
        prev_value = self._prev_value
        on_value = self.widget.cget("onvalue")
        self.emit(Event.CHANGED, checked=value == on_value, value=value, prev_value=prev_value)
        self._prev_value = value

    def on_changed(
            self, handler: Optional[EventHandler] = None,
            *, scope="widget") -> Stream[Any] | Self:
        """Stream or chainable binding for <<Changed>>

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """
        stream = self.on(Event.CHANGED, scope=scope)
        if handler is None:
            return stream
        stream.listen(coerce_handler_args(handler))
        return self

    def on_invoke(
            self, handler: Optional[AltEventHandler] = None,
            *, scope="widget") -> Stream[Any] | Self:
        """Stream or chainable binding for <<Invoke>>

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """
        stream = self.on(Event.INVOKE, scope=scope)
        if handler is None:
            return stream
        stream.listen(coerce_handler_args(handler))
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
        """Get or set the signal controlling the checkbutton value."""
        if value is None:
            return self._value_signal
        # change signals
        if self._on_changed_fid:
            self._value_signal.unsubscribe(self._on_changed_fid)
        self._value_signal = value
        self.configure(variable=self._value_signal.var)
        self._on_changed_fid = self._value_signal.subscribe(self._handle_change)
        self._prev_value = self._value_signal()
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

    def invoke(self):
        """Trigger the checkbutton as if it were toggled."""
        self.widget.invoke()
        return self

    def is_checked(self):
        """Return True if the current value matches the on_value."""
        return 'selected' in self.widget.state()

    def destroy(self):
        """Unsubscribe callbacks and destroy the widget."""
        if self._on_changed_fid:
            self._value_signal.unsubscribe(self._on_changed_fid)
            self._on_changed_fid = None
        super().destroy()
