from typing import Any, Callable, Union
from tkinter import ttk

from ttkbootstrap.core import Signal
from ttkbootstrap.core.widget import BaseWidget


class Slider(BaseWidget):
    _configure_methods = {"signal", "value", "min_value", "max_value", "precision", "on_change"}

    def __init__(
            self,
            parent,
            value: int | float = 0.0,
            min_value: int | float = 0.0,
            max_value: int | float = 100.0,
            precision: int = 0,
            on_change: Callable[[float], Any] = None,
            **kwargs
    ):
        """Create a new Slider widget with a signal-based value and callback.

        Args:
            parent: The parent widget.
            value: The initial value of the slider.
            min_value: The minimum value for the slider.
            max_value: The maximum value for the slider.
            precision: The number of decimal places to round the value.
            on_change: Optional callback invoked when the value changes.
            **kwargs: Additional keyword arguments passed to ttk.Scale.
        """
        self._signal = Signal(value)
        self._on_change = on_change
        self._on_change_fid = None
        self._precision = precision
        self._prev_value = round(value, precision)

        self._widget = ttk.Scale(
            parent,
            from_=min_value,
            to=max_value,
            variable=self._signal.var,
            **kwargs
        )
        super().__init__(parent)
        if on_change:
            self._on_change_fid = self.on_change(self._on_change)

    def signal(self, value: Signal = None):
        """Get or set the signal controlling the slider value."""
        if value is None:
            return self._signal
        else:
            if self._on_change_fid:
                self._signal.unsubscribe(self._on_change_fid)
            self._signal = value
            self.configure(variable=value)
            if self._on_change:
                self._on_change_fid = value.subscribe(self._on_change)
            return self

    def value(self, value: int | float = None):
        """Get or set the current slider value."""
        if value is None:
            return self._signal()
        else:
            self._signal.set(value)
            return self

    def min_value(self, value: int | float = None):
        """Get or set the minimum value for the slider."""
        if value is None:
            return self.configure("from_")
        else:
            self.configure(from_=value)
            return self

    def max_value(self, value: int | float = None):
        """Get or set the maximum value for the slider."""
        if value is None:
            return self.configure("to")
        else:
            self.configure(to=value)
            return self

    def precision(self, value: int = None):
        """Get or set the number of decimal places for rounding."""
        if value is None:
            return self._precision
        else:
            if not isinstance(value, int) or value < 0:
                raise ValueError("precision must be a non-negative integer")
            self._precision = value
            self._prev_value = round(self._signal(), value)
            return self

    def _handle_change(self, raw_value: int | float):
        """Handle internal value change and invoke callback if needed."""
        rounded = round(raw_value, self._precision)
        if rounded == self._prev_value:
            return "break"
        else:
            self._prev_value = rounded
            if self._on_change:
                return self._on_change(rounded)
        return "break"

    def on_change(self, func: Callable[[Union[int, float]], Any] = None):
        """Get or set the callback triggered on significant value change."""
        if func is None:
            return self._on_change
        else:
            if func is not None and not callable(func):
                raise TypeError(f"`on_change` must be callable, got {type(func).__name__}")
            if self._on_change_fid:
                self._signal.unsubscribe(self._on_change_fid)
                self._on_change_fid = None
            self._on_change = func
            if func:
                self._on_change_fid = self._signal.subscribe(self._handle_change)
            return self

    def destroy(self):
        """Unsubscribe signal listeners and destroy the slider widget."""
        if self._on_change_fid:
            self._signal.unsubscribe(self._on_change_fid)
            self._on_change_fid = None
        super().destroy()
