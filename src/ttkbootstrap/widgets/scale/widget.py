from decimal import Decimal, ROUND_HALF_UP
from tkinter import ttk
from typing import Any, Callable, Optional, Unpack

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.events import Event
from ttkbootstrap.interop.runtime.binding import Stream, Subscription
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.style.types import SemanticColor
from ttkbootstrap.types import Orientation, Variable
from ttkbootstrap.widgets.scale.events import ScaleChangedEvent
from ttkbootstrap.widgets.scale.style import ScaleStyleBuilder
from ttkbootstrap.widgets.scale.types import ScaleOptions


class Scale(BaseWidget):
    widget: ttk.Scale

    _configure_methods = {
        "color": "_configure_color",
        "min_value": "_configure_min_value",
        "max_value": "_configure_max_value",
        "precision": "_configure_precision",
        "variable": "_configure_variable",
        "signal": "_configure_signal",
        "command": "_configure_command"
    }

    def __init__(
            self,
            value: int | float | Signal = 0.0,
            min_value: int | float = 0.0,
            max_value: int | float = 100.0,
            precision: int = 0,
            *,
            step: float | None = None,
            color: SemanticColor = "primary",
            orient: Orientation = "horizontal",
            command: Optional[Callable] = None,
            **kwargs: Unpack[ScaleOptions],
    ):
        """Create a new Scale widget bound to a Signal.

        Args:
            value: Initial value or a `Signal[int | float]`.
            min_value: Lower bound (inclusive).
            max_value: Upper bound (inclusive).
            precision: Decimal places for rounding/display (0 = integer).

        Keyword Args:
            step: Increment for keyboard/programmatic changes; None uses native ttk.
            color: Semantic color (e.g., "primary").
            orient: "horizontal" or "vertical".
            command: Callback invoked with the new float value.
            cursor: The cursor that appears when the mouse is over the widget.
            id: A unique identifier used to query this widget.
            length: The length of the progress bar in pixels.
            orient: Indicates whether the widget should be laid or horizontally or vertically.
            parent: The parent container of this widget.
            position: The `place` container position.
            take_focus: Indicates whether the widget accepts focus during keyboard traversal.
            variable: A tkinter variable bound to the widget value.
        """
        self._style_builder = ScaleStyleBuilder(color=color, orient=orient)
        self._value_signal = value if isinstance(value, Signal) else Signal(value)
        self._precision = int(precision)
        self._step = step
        self._in_change = False
        self._value_signal_sub: Any = None
        self._prev_value: int | float = 0
        self._command = command
        self._command_sub: Optional[Subscription] = None

        parent = kwargs.pop("parent", None)
        tk_options = {
            "from_": min_value,
            "to": max_value,
            "orient": orient,
            "variable": self._value_signal.var,
            **kwargs,
        }
        super().__init__(ttk.Scale, tk_options, parent=parent)

        # Baseline after Tk options are live (so min/max are readable)
        self._prev_value = self._normalize_value(float(self._value_signal()))

        # Subscribe to signal to enforce normalization and emit events
        self._value_signal_sub = self._value_signal.subscribe(self._handle_change)

        # Focus on click (nice UX)
        self.on(Event.CLICK).listen(self.focus)

        # Mouse wheel support
        self._bind_mouse_wheel()

        if command:
            self._configure_command(command)

        self._value_signal_sub = self._value_signal.subscribe(self._handle_change)

    def signal(self):
        """The signal bound to the widget value"""
        return self._value_signal

    def value(self, value: int | float = None):
        """Get or set the current slider value (normalized)."""
        if value is None:
            return self._value_signal()
        else:
            coerced = self._coerce_for_signal(value)
            self._value_signal.set(coerced)
            return self

    def destroy(self):
        """Unsubscribe listeners and destroy the widget."""
        if self._value_signal_sub is not None:
            try:
                self._value_signal.unsubscribe(self._value_signal_sub)
            except Exception:
                pass
            self._value_signal_sub = None
        super().destroy()

    # ----- Configuration delegates -----

    def _configure_command(self, value: Callable[..., Any] = None):
        if value is None:
            return self._command
        else:
            if self._command_sub:
                self._command_sub.unlisten()
            self._command_sub = self.on_changed().tap(lambda _: value()).then_stop()
            return self

    def _configure_color(self, value: SemanticColor = None):
        if value is None:
            return self._style_builder.options('color')
        else:
            self._style_builder.options(color=value)
            self.update_style()
            return self

    def _configure_value_signal(self, value: Signal = None):
        """Get or set the slider Signal."""
        if value is None:
            return self._value_signal
        else:
            if self._value_signal_sub is not None:
                self._value_signal.unsubscribe(self._value_signal_sub)
            self._value_signal = value
            self.configure(variable=value.var)
            self._prev_value = self._normalize_value(float(self._value_signal()))
            self._value_signal_sub = self._value_signal.subscribe(self._handle_change)
            return self

    def _configure_min_value(self, value: int | float = None):
        """Get or set the minimum value."""
        if value is None:
            return self.configure("from_")
        else:
            self.configure(from_=value)
            self._prev_value = self._normalize_value(float(self._value_signal()))
            return self

    def _configure_max_value(self, value: int | float = None):
        """Get or set the maximum value."""
        if value is None:
            return self.configure("to")
        else:
            self.configure(to=value)
            self._prev_value = self._normalize_value(float(self._value_signal()))
            return self

    def _configure_precision(self, value: int = None):
        """Get or set decimal precision (ignored in int mode)."""
        if value is None:
            return self._precision
        else:
            if not isinstance(value, int) or value < 0:
                raise ValueError("precision must be a non-negative integer")
            self._precision = value
            self._prev_value = self._normalize_value(float(self._value_signal()))
            return self

    def _configure_variable(self, value: Variable = None):
        if value is None:
            return self._value_signal
        else:
            return self._configure_value_signal(Signal.from_variable(value))

    # ----- Event handlers ------

    def on_changed(self) -> Stream[ScaleChangedEvent]:
        """Convenience alias for changed stream"""
        return self.on(Event.CHANGED)

    def _handle_change(self, raw_value: int | float):
        """Normalize, snap-back if needed, and emit <<Changed>> with value/prev_value."""
        if self._in_change:
            return "break"
        self._in_change = True
        try:
            snapped = self._normalize_value(float(raw_value))

            # If normalization changed the value, write it back to the Signal (updates UI)
            if snapped != raw_value and snapped != self._value_signal():
                self._value_signal.set(snapped)

            # Only emit when the stable value changes
            if snapped != self._prev_value:
                prev = self._prev_value
                self._prev_value = snapped
                self.emit(Event.CHANGED, value=snapped, prev_value=prev)

            return "break"
        finally:
            self._in_change = False

    # ------ Helpers -----

    def _signal_type(self):
        """Declared Signal type if present, else type(value)."""
        return getattr(self._value_signal, "_type", type(self._value_signal()))

    def _effective_dtype(self) -> type[int] | type[float]:
        """Infer dtype strictly from the bound Signal."""
        return int if self._signal_type() is int else float

    def _effective_step(self) -> float | None:
        """Default step=1.0 for int mode if not provided."""
        return self._step if self._step is not None else (1.0 if self._effective_dtype() is int else None)

    def _normalize_value(self, v: float) -> int | float:
        """Clamp → step snap → precision → cast per inferred dtype."""
        min_ = float(self._configure_min_value())
        max_ = float(self._configure_max_value())
        dtype = self._effective_dtype()
        step = self._effective_step()
        precision = 0 if dtype is int else max(0, int(self._precision))

        # clamp
        v = min(max(v, min_), max_)
        d = Decimal(str(v))
        dmin = Decimal(str(min_))

        # snap
        if step is not None and step > 0:
            dstep = Decimal(str(step))
            q = ((d - dmin) / dstep).to_integral_value(rounding=ROUND_HALF_UP)
            d = dmin + q * dstep

        # round (floats only)
        if precision is not None and precision >= 0:
            d = d.quantize(Decimal(1).scaleb(-precision), rounding=ROUND_HALF_UP)

        return int(d) if dtype is int else float(d)

    def _coerce_for_signal(self, val: float | int):
        return self._normalize_value(float(val))

    def _bind_mouse_wheel(self) -> None:
        """Bind mouse wheel to change value (X11 uses Button-4/5; Win/mac use MouseWheel)."""
        if self.windowing_system() in ("win32", "aqua"):
            self.on(Event.MOUSE_WHEEL).listen(self._on_mousewheel_windows_mac)
        else:
            self.on(Event.WHEEL_UP).listen(self._on_mousewheel_x11)
            self.on(Event.WHEEL_DOWN).listen(self._on_mousewheel_x11)

    def _wheel_step(self, event=None) -> float:
        """
        Base step:
          - explicit step if set,
          - else 1 for int signals,
          - else 10^-precision for float signals.
        Hold Shift for 10x.
        """
        base = self._effective_step()
        if base is None:
            base = 1.0 if self._precision == 0 else (10 ** (-self._precision))
        if event is not None and (getattr(event, "state", 0) & 0x0001):  # Shift
            base *= 10
        return base

    def _apply_delta(self, delta: float) -> str:
        cur = float(self.value())
        new_val = self._normalize_value(cur + delta)
        if new_val != cur:
            self.value(new_val)
        return "break"

    def _orientation_sign(self, scroll_up: bool) -> float:
        """Map scroll direction to +/- considering orientation and range direction."""
        inc_dir = 1.0 if self._configure_min_value() < self._configure_max_value() else -1.0
        if str(self.configure("orient")) == "vertical":
            return (-inc_dir) if scroll_up else (+inc_dir)
        else:
            return (+inc_dir) if scroll_up else (-inc_dir)

    def _on_mousewheel_windows_mac(self, event) -> str:
        step = self._wheel_step(event)
        scroll_up = (event.delta > 0)
        sgn = self._orientation_sign(scroll_up)
        return self._apply_delta(sgn * step)

    def _on_mousewheel_x11(self, event) -> str:
        step = self._wheel_step(event)
        scroll_up = (event.num == 4)  # 4=up, 5=down
        sgn = self._orientation_sign(scroll_up)
        return self._apply_delta(sgn * step)
