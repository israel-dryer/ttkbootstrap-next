from __future__ import annotations

from typing import Any, Optional, Self, Unpack

from ttkbootstrap_next.events import Event
from ttkbootstrap_next.interop.runtime.configure import configure_delegate
from ttkbootstrap_next.localization.intl_format import FormatSpec, IntlFormatter
from ttkbootstrap_next.signals.signal import Signal
from ttkbootstrap_next.types import Number, Variable
from ttkbootstrap_next.utils import assert_valid_keys, encode_event_value_data
from ttkbootstrap_next.widgets.entry.shared.entry_part import EntryOptions, EntryPart


class ManualNumericPart(EntryPart):
    """
    Numeric entry built on top of EntryPart with manual stepping.

    - Keeps a numeric model value; display is always derived from the model
      via `value_format` on commit and on each step.
    - Supports min/max, increment, optional wrap, keyboard Up/Down and wheel
      bindings, and Increment/Decrement virtual events.
    - Works with percent/currency/custom number specs without Tk printf limits.
    """

    def __init__(
            self,
            value: Number | Signal | str = 0,
            *,
            value_format: Optional[FormatSpec] = None,
            allow_blank: bool = True,
            min_value: Number = 0,
            max_value: Number = 100,
            increment: Number = 1,
            wrap: bool = False,
            initial_focus: bool = False,
            **kwargs: Unpack[EntryOptions],
    ):
        # Extract entry kwargs and validate
        parent = kwargs.pop("parent", None)
        assert_valid_keys(kwargs, EntryOptions, where="ManualNumericPart")

        # Configure numeric settings
        self._min = min_value
        self._max = max_value
        self._inc = increment
        self._wrap = bool(wrap)
        # Allow per-widget locale via EntryOptions (kept in kwargs)
        locale_arg = kwargs.get("locale", None)
        self._fmt = IntlFormatter(locale=locale_arg)
        self._num_type = float if any(
            isinstance(x, float) or (isinstance(x, (int, float)) and float(x) != int(x))
            for x in (min_value, max_value, increment, value if not isinstance(value, Signal) else 0)
        ) else int

        # Let EntryPart parse/format initial state and wire base behavior
        super().__init__(
            value=value,
            value_format=value_format,
            allow_blank=allow_blank,
            initial_focus=initial_focus,
            parent=parent,
            **kwargs,
        )

        # Bind virtual increment/decrement
        self.on(Event.INCREMENT).listen(lambda _: self.step(+1))
        self.on(Event.DECREMENT).listen(lambda _: self.step(-1))

        # Keyboard: Up/Down adjust value; stop propagation for a crisp UX
        self.on(Event.KEYDOWN_UP).tap(lambda _: self.step(+1)).then_stop()
        self.on(Event.KEYDOWN_DOWN).tap(lambda _: self.step(-1)).then_stop()

        # Wheel support (Windows/macOS): use delta sign
        def on_wheel(e: Any):
            try:
                d = int(getattr(e, "delta", 0))
            except Exception:
                d = 0
            if d != 0:
                self.step(+1 if d > 0 else -1)

        self.on(Event.MOUSE_WHEEL).listen(on_wheel)

        # Wheel support (X11): button-4/5
        self.on(Event.WHEEL_UP).listen(lambda _: self.step(+1))
        self.on(Event.WHEEL_DOWN).listen(lambda _: self.step(-1))

    # ---- Public numeric API ----
    def step(self, n: int = 1) -> Self:
        """Increment/decrement by n steps and update display + events."""
        prev = self._value

        base = 0 if prev is None else float(prev)
        next_val = base + float(self._inc) * float(n)

        # Clamp or wrap
        next_val = self._apply_bounds(next_val)

        # Coerce to desired type
        coerced = float(next_val) if self._num_type is float else int(round(next_val))

        # Update model and display
        self._value = coerced
        self._normalize_display_from_value()

        # Emit CHANGED if the numeric value actually changed
        if self._value != self._prev_changed_value:
            self.emit(
                Event.CHANGED,
                value=encode_event_value_data(self._value),
                prev_value=encode_event_value_data(self._prev_changed_value),
                text=self._signal(),
            )
            self._prev_changed_value = self._value

        return self

    # ---- Internals ----
    def _apply_bounds(self, x: float) -> float:
        lo, hi = float(self._min), float(self._max)
        if not self._wrap:
            return min(max(x, lo), hi)
        if hi <= lo:
            return lo
        span = hi - lo
        # Normalize with wrap (handle large jumps gracefully)
        while x < lo:
            x += span
        while x > hi:
            x -= span
        return x

    def _normalize_display_from_value(self) -> None:
        # Compute formatted text per EntryPart behavior
        if self._value is None:
            new_text = ""
        else:
            vf = getattr(self, "_value_format", None)
            if vf is None:
                new_text = str(self._value)
            else:
                new_text = self._fmt.format(float(self._value), vf)

        if new_text != self._signal():
            # Avoid feeding back a spurious INPUT
            fid = getattr(self, "_on_input_fid", None)
            if fid:
                try:
                    self._signal.unsubscribe(fid)
                except Exception:
                    pass
            self._signal.set(new_text)
            if fid:
                self._on_input_fid = self._signal.subscribe(self._handle_change)

    # Override to expose strong typing in configure API
    @configure_delegate("text_variable")
    @configure_delegate("textvariable")
    def _configure_text_variable(self, value: Variable = None):
        if value is None:
            return self._signal
        else:
            return self._configure_signal(Signal.from_variable(value))
