from tkinter import ttk
from typing import Any, Callable, Optional, Self, Union, Unpack

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.events import Event
from ttkbootstrap.interop.runtime.binding import Stream
from ttkbootstrap.interop.runtime.utils import coerce_handler_args
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.style.builders.radio_button import RadioButtonStyleBuilder
from ttkbootstrap.style.types import ForegroundColor
from ttkbootstrap.types import AltEventHandler, CoreOptions, EventHandler


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
        "readonly": "readonly"
    }

    def __init__(
            self,
            text: str = "",
            value: str | int = 0,
            group: Union[str, Signal] = None,
            color: ForegroundColor = "primary",
            selected: bool = False,
            on_invoke: Callable[[AltEventHandler], Any] = None,
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
            on_invoke: Callback fired when the button is invoked.
            **kwargs: Additional keyword arguments.
        """
        self._style_builder = RadioButtonStyleBuilder(color=color, variant=variant)
        self._text_signal = Signal(text)

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
            command=self._handle_invoke,
            **kwargs
        )
        super().__init__(ttk.Radiobutton, tk_options, parent=parent)

        if selected:
            self.select()

        if on_invoke:
            self.on_invoke(on_invoke)
        self._on_changed_fid = self._value_signal.subscribe(self._handle_change)

    def _handle_invoke(self):
        """Trigger <<Invoke>> when the button is activated"""
        self.emit(Event.INVOKE, selected=self.is_selected(), value=self._value_signal())

    def _handle_change(self, _: Any):
        """Trigger <<RadioSelected>> / <<RadioDeselected>> on group value changes."""
        value = self._value_signal()
        prev_value = self._prev_value
        # Coerce widget value to signal's type before comparison
        on_value = self._coerce_to_signal_type(self.widget.cget("value"))

        if value == on_value and prev_value != on_value:
            self.emit(Event.RADIO_SELECTED, selected=True, value=value, prev_value=prev_value)
        elif prev_value == on_value and value != on_value:
            self.emit(Event.RADIO_DESELECTED, selected=False, value=value, prev_value=prev_value)

        self._prev_value = value

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
        # change signals
        if self._on_changed_fid:
            self._value_signal.unsubscribe(self._on_changed_fid)
        self._value_signal = value
        self.configure(variable=self._value_signal.var)
        self._on_changed_fid = self._value_signal.subscribe(self._handle_change)
        self._prev_value = self._value_signal()
        return self

    def on_selected(
            self, handler: Optional[EventHandler] = None,
            *, scope="widget") -> Stream[Any] | Self:
        """Stream or chainable binding for <<Selected>>>>

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """
        stream = self.on(Event.RADIO_SELECTED, scope=scope)
        if handler is None:
            return stream
        stream.listen(coerce_handler_args(handler))
        return self

    def on_deselected(
            self, handler: Optional[EventHandler] = None,
            *, scope="widget") -> Stream[Any] | Self:
        """Stream or chainable binding for <<Deselected>>>>

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """
        stream = self.on(Event.RADIO_DESELECTED, scope=scope)
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
        if self._on_changed_fid:
            self._value_signal.unsubscribe(self._on_changed_fid)
            self._on_changed_fid = None
        super().destroy()

    def _coerce_to_signal_type(self, v):
        # Align the radiobutton's 'value' with the group's Signal[T] type
        t = getattr(self._value_signal, "_type", None)
        if t is int:   return int(v)
        if t is float: return float(v)
        if t is str:   return str(v)
        try:
            # best-effort fallback
            return t(v) if t else v
        except Exception:
            return v
