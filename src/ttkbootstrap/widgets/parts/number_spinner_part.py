from tkinter.font import Font
from typing import Any, Callable, Optional, Self, Unpack

from tkinter import ttk

from ttkbootstrap.interop.runtime.binding import Stream
from ttkbootstrap.interop.runtime.utils import coerce_handler_args
from ttkbootstrap.types import Justify, Padding, CoreOptions, Number
from ttkbootstrap.events import Event
from ttkbootstrap.utils import assert_valid_keys
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.widgets.mixins.entry_mixin import EntryMixin
from ttkbootstrap.widgets.mixins.validatable_mixin import ValidationMixin
from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.style.builders.spinbox import SpinBoxStyleBuilder


class SpinboxOptions(CoreOptions, total=False):
    """
    Options for configuring a number spinner widget.

    Attributes:
        cursor: The cursor that appears when the mouse is over the widget.
        font: The font used to render text in the entry (name or Font object).
        foreground: The text color (e.g., "#333", "red").
        take_focus: Indicates whether the widget accepts focus during keyboard traversal.
        x_scroll_command: A callback used to link the entry to a horizontal scrollbar.
        export_selection: Whether to export the selection to the clipboard (default is True).
        justify: Text justification (left, center, or right).
        show: The character used to mask text (e.g., "*" for passwords).
        width: The width of the entry widget in characters.
    """
    cursor: str
    font: str | Font
    foreground: str
    take_focus: bool
    x_scroll_command: Callable
    export_selection: bool
    justify: Justify
    show: str
    width: int
    padding: Padding
    format: str


class SpinboxPart(ValidationMixin, EntryMixin, BaseWidget):
    """A numeric spinbox widget with signal binding and validation support.

    This widget wraps a `ttk.Spinbox` and binds it to a reactive `Signal`,
    supporting live value updates, focus-based change detection, and validation hooks.

    Args:
        parent: The parent widget.
        value: Initial numeric value (default is 0).
        on_change: Callback triggered on every value change (live).
        on_enter: Callback triggered when Enter is pressed.
        min_value: Minimum value of the spinbox (default is 0).
        max_value: Maximum value of the spinbox (default is 100).
        increment: Step size for value changes (default is 1).
        formatter: Optional format string for display (e.g., "%.1f").
        wrap: Whether the value should wrap at min/max (default is False).
        initial_focus: Whether the widget receives focus initially.
        **kwargs: Additional keyword arguments.
    """

    widget: ttk.Spinbox

    _configure_methods = {
        "value": "value",
        "formatter": "formatter",
        "signal": "signal",
        "readonly": "readonly"
    }

    def __init__(
            self,
            value: Number | Signal = 0,
            on_change: Callable[[Any], Number] = None,
            on_enter: Callable[[Any], Number] = None,
            min_value: Number = 0,
            max_value: Number = 100,
            increment: Number = 1,
            formatter: str = None,
            wrap: bool = False,
            initial_focus: bool = False,
            **kwargs: Unpack[SpinboxOptions]
    ):
        self._style_builder = SpinBoxStyleBuilder()
        self._on_change = None
        self._on_change_fid = None

        # coerce signal and signal type
        if isinstance(value, Signal):
            self._signal = value
            self._prev_value = value()
        else:
            self._prev_value, increment = self._coerce_signal_value(value, increment)
            self._signal = Signal(self._prev_value)

        assert_valid_keys(kwargs, SpinboxOptions, where="SpinboxPart")

        parent = kwargs.pop('parent', None)
        kwargs.setdefault("from", min_value)
        kwargs.setdefault("to", max_value)
        kwargs.setdefault("increment", increment)
        kwargs.setdefault("wrap", str(wrap).lower())

        if formatter:
            try:
                _ = formatter % float(value)
            except Exception:
                raise ValueError(f"Invalid formatter: {formatter!r}")
            kwargs.update(format=formatter)

        tk_options = dict(textvariable=self._signal.var, **kwargs)
        super().__init__(ttk.Spinbox, tk_options, parent=parent)

        if on_change:
            self.on_change(on_change)

        if on_enter:
            self.on_enter(on_enter)

        self.bind(Event.FOCUS, self._store_prev_value)
        self.bind(Event.BLUR, self._check_if_changed)

        if initial_focus:
            self.focus()

    @staticmethod
    def _coerce_signal_value(value, increment):
        """Ensure signal is setup with appropriate data type"""
        if isinstance(value, float) or isinstance(increment, float):
            return float(value or 0), float(increment)
        return int(value or 0), int(increment)

    def _store_prev_value(self, _: Any):
        """Store the current value before focus out."""
        self._prev_value = self._signal()

    def _check_if_changed(self, _: Any):
        """Emit the 'changed' event if the value was modified after focus out."""
        try:
            current = self._signal()
            if self._prev_value is not None and current != self._prev_value:
                self.emit(Event.CHANGED)
        except (ValueError, TypeError):
            pass

    def value(self, value: Number = None):
        """Get or set the current value of the spinbox."""
        if value is None:
            return self._signal()
        self._signal.set(value)
        return self

    def formatter(self, value: str = None):
        if value is None:
            return self.widget.cget('format')
        else:
            try:
                _ = value % float(value)
            except Exception:
                raise ValueError(f"Invalid formatter: {value!r}")
            self.configure(format=value)
            return self

    def signal(self, value: Signal[Number] = None):
        """Get or set the bound signal."""
        if value is None:
            return self._signal
        self._signal = value
        self.configure(textvariable=self._signal.var)
        return self

    def on_change(self, value: Callable[[int | float], Any] = None):
        """Bind or set the <<Change>> event handler."""
        if value is None:
            return self._on_change
        else:
            self._on_change = value
            self._on_change_fid = self._signal.subscribe(lambda _: self._on_change(self._signal()))
            return self

    def on_enter(
            self, handler: Optional[Callable] = None,
            *, scope="widget") -> Stream[Any] | Self:
        """Stream or chainable binding for <Return>

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """
        stream = self.on(Event.RETURN, scope=scope)
        if handler is None:
            return stream
        stream.listen(coerce_handler_args(handler))
        return self

    def on_changed(
            self, handler: Optional[Callable[[Any], Any]] = None,
            *, scope="widget") -> Stream[Any] | Self:
        """Stream or chainable binding for <<Changed>>

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """
        stream = self.on(Event.CHANGED, scope=scope)
        if handler is None:
            return stream
        stream.listen(handler)
        return self

    def destroy(self) -> None:
        """Unsubscribe from signal and destroy the widget."""
        if self._on_change_fid:
            self._signal.unsubscribe(self._on_change_fid)
            self._on_change_fid = None
        super().destroy()
