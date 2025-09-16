from tkinter import ttk
from typing import Any, Callable, Union, Unpack

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.events import Event
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.style.types import SemanticColor
from ttkbootstrap.types import Orientation
from ttkbootstrap.widgets.scale.style import ScaleStyleBuilder
from ttkbootstrap.widgets.scale.types import ScaleOptions


class Scale(BaseWidget):
    widget: ttk.Scale
    _configure_methods = {
        "value": "value",
        "min_value": "min_value",
        "max_value": "max_value",
        "precision": "precision",
    }

    def __init__(
            self,
            value: int | float | Signal = 0.0,
            min_value: int | float = 0.0,
            max_value: int | float = 100.0,
            precision: int = 0,
            color: SemanticColor = "primary",
            orient: Orientation = "horizontal",
            on_change: Callable[[float], Any] = None,
            **kwargs: Unpack[ScaleOptions]
    ):
        """Create a new Scale widget with a signal-based value and callback.

        Args:
            parent: The parent widget.
            value: The initial value of the slider.
            min_value: The minimum value for the slider range.
            max_value: The maximum value for the slider range.
            precision: The number of decimal places to round the value.
            color: The color used to theme the slider (e.g., "primary", "info").
            orient: The orientation of the slider; either "horizontal" or "vertical".
            on_change: Optional callback invoked with the rounded value when the value changes significantly.
            **kwargs: Additional options supported by Scale.
        """
        self._style_builder = ScaleStyleBuilder(color=color, orient=orient)
        self._signal = value if isinstance(value, Signal) else Signal(value)
        self._on_change = on_change
        self._on_change_fid = None
        self._precision = precision

        cur = self._signal()
        self._prev_value = round(float(cur), precision)

        parent = kwargs.pop("parent", None)

        tk_options = {
            "from_": min_value,
            "to": max_value,
            "orient": orient,
            "variable": self._signal.var,
            **kwargs
        }
        super().__init__(ttk.Scale, tk_options, parent=parent)
        if on_change:
            self._on_change_fid = self.on_change(self._on_change)

        # receive focus when clicked
        self.on(Event.CLICK).listen(self.focus)

        # add mouse wheel scaling
        self._bind_mouse_wheel()

    def _signal_type(self):
        # Many Signal impls expose a _type; fall back to current value type
        return getattr(self._signal, "_type", type(self._signal()))

    def _coerce_for_signal(self, val: float | int):
        t = self._signal_type()
        if t is int:
            # int signal: round to precision then cast to int
            return int(round(val))
        # float (or other): round to configured precision
        return round(float(val), self._precision)

    def _bind_mouse_wheel(self) -> None:
        """Bind mouse wheel to change value (X11 uses Button-4/5; Win/mac use MouseWheel)."""

        # Windows/macOS use <MouseWheel>, Linux/X11 uses Button-4/5 for scroll
        if self.windowing_system() in ("win32", "aqua"):
            self.on(Event.MOUSE_WHEEL).listen(self._on_mousewheel_windows_mac)
        else:  # x11
            self.on(Event.WHEEL_UP).listen(self._on_mousewheel_x11)
            self.on(Event.WHEEL_DOWN).listen(self._on_mousewheel_x11)

    def _wheel_step(self, event=None) -> float:
        """Base step derived from precision; hold Shift for 10x."""
        base = 1.0 if self._precision == 0 else (10 ** (-self._precision))
        if event is not None and (getattr(event, "state", 0) & 0x0001):  # Shift modifier
            base *= 10
        return base

    def _apply_delta(self, delta: float) -> str:
        """Apply delta, clamped to [min,max], and respect precision."""
        cur = self.value()
        new_val = cur + delta
        new_val = max(self.min_value(), min(self.max_value(), new_val))
        self.value(self._coerce_for_signal(new_val))
        return "break"

    def _orientation_sign(self, scroll_up: bool) -> float:
        """
        Convert scroll direction to +/- delta sign, considering orientation and range.
        Goal: 'scroll up' should move the indicator UP for vertical, RIGHT for horizontal.
        """
        # +1 means "increase value" when min<max, -1 means "decrease value"
        inc_dir = 1.0 if self.min_value() < self.max_value() else -1.0

        if str(self.configure("orient")) == "vertical":
            # For vertical: UP should move the indicator UP.
            # With the usual min<max, increasing moves the thumb DOWN,
            # so invert: scroll_up => DECREASE (i.e., -inc_dir)
            return (-inc_dir) if scroll_up else (+inc_dir)
        else:
            # For horizontal: UP should INCREASE (move right)
            return (+inc_dir) if scroll_up else (-inc_dir)

    def _on_mousewheel_windows_mac(self, event) -> str:
        """Handle <MouseWheel> on Windows/macOS."""
        step = self._wheel_step(event)
        # Windows: event.delta is multiples of 120; macOS: ±1 or small values.
        scroll_up = (event.delta > 0)
        sgn = self._orientation_sign(scroll_up)
        return self._apply_delta(sgn * step)

    def _on_mousewheel_x11(self, event) -> str:
        """Handle Button-4 (up) / Button-5 (down) on X11/Linux."""
        step = self._wheel_step(event)
        scroll_up = (event.num == 4)  # 4 = up, 5 = down
        sgn = self._orientation_sign(scroll_up)
        return self._apply_delta(sgn * step)

    def signal(self, value: Signal = None):
        """Get or set the slider value signal."""
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
            coerced = self._coerce_for_signal(value)
            self._signal.set(coerced)
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
