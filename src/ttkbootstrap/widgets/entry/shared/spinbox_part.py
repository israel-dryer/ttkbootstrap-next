from __future__ import annotations

from tkinter import ttk
from typing import Any, Optional, Self, Unpack

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.events import Event
from ttkbootstrap.interop.runtime.binding import Scope, Stream
from ttkbootstrap.localization.intl_format import FormatSpec, IntlFormatter
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.types import EventHandler, Number
from ttkbootstrap.utils import assert_valid_keys, encode_event_value_data
from ttkbootstrap.widgets.entry.events import SpinboxChangedEvent, SpinboxEnterEvent, SpinboxInputEvent
from ttkbootstrap.widgets.entry.shared.entry_mixin import EntryMixin
from ttkbootstrap.widgets.entry.shared.validatable_mixin import ValidationMixin
from ttkbootstrap.widgets.entry.style import SpinBoxStyleBuilder
from ttkbootstrap.widgets.entry.types import SpinboxOptions


class SpinboxPart(ValidationMixin, EntryMixin, BaseWidget):
    """
    Intl-aware **numeric** Spinbox that cleanly separates **typed text** (`display`)
    from the **committed/parsed value** (`value`). Parsing/formatting happens only on
    commit (blur or Enter), keeping typing snappy.

    Notes
    -----
    - `display_format` is restricted to *number* formats (validation occurs on set).
    - Live edits emit `<<Input>>` with `text` only (no parsing).
    - On blur/Enter we `commit()` once, normalize display text, and emit `<<Changed>>`
      *only if* the parsed number actually changed since focus-in.
    """

    widget: ttk.Spinbox

    _configure_methods = {
        "value": "value",
        "display": "display",
        "display_format": "display_format",
        "allow_blank": "allow_blank",
        "readonly": "readonly",
        "commit": "commit",
    }

    def __init__(
            self,
            value: Number | Signal = 0,
            *,
            # Intl number formatting (e.g., compact, grouping, precision) — numbers only
            display_format: Optional[FormatSpec] = None,
            allow_blank: bool = True,
            # Spin constraints
            min_value: Number = 0,
            max_value: Number = 100,
            increment: Number = 1,
            wrap: bool = False,
            # Events
            on_input: EventHandler = None,  # fires with text only (every edit)
            on_enter: EventHandler = None,  # fires after commit
            initial_focus: bool = False,
            **kwargs: Unpack[SpinboxOptions],
    ):
        self._style_builder = SpinBoxStyleBuilder()

        # Intl engine
        self._fmt = IntlFormatter()
        self._display_format = None  # set via setter to validate "numbers only"
        self._value: Optional[Number] = None
        self.display_format(display_format)  # validates number-only spec

        self._allow_blank = bool(allow_blank)

        # Decide numeric coercion kind upfront (int vs float) from inputs
        self._num_type = float if any(
            isinstance(x, float) or (isinstance(x, (int, float)) and float(x) != int(x))
            for x in (min_value, max_value, increment, value if not isinstance(value, Signal) else 0)
        ) else int

        # Establish initial display + parsed value
        if isinstance(value, Signal):
            initial_display = value()
            self._signal = value  # display-level signal (text)
            initial_value = self._parse_number_or_none(str(initial_display))
        elif isinstance(value, (int, float)):
            initial_value = value
            initial_display = (
                str(value) if self._display_format is None
                else self._fmt.format(float(value), self._display_format)
            )
            self._signal = Signal(initial_display)
        else:
            # Fallback — treat as text, try to parse into number
            initial_display = "" if value is None else str(value)
            initial_value = self._parse_number_or_none(initial_display)
            self._signal = Signal(initial_display)

        # Keep the committed numeric value separate from display text
        self._value: Optional[Number] = None if initial_value is None else self._coerce_num(initial_value)
        self._prev_changed_value = self._value

        # Normalize initial display if we already have a parsed value
        if self._value is not None:
            self._signal.set(self._format_number(self._value))

        # Tk options
        parent = kwargs.pop("parent", None)
        assert_valid_keys(kwargs, SpinboxOptions, where="SpinboxPart")
        kwargs.setdefault("from", min_value)
        kwargs.setdefault("to", max_value)
        kwargs.setdefault("increment", self._num_type(increment))  # coerce increment to datatype
        kwargs.setdefault("wrap", str(bool(wrap)).lower())

        tk_options = dict(textvariable=self._signal.var, **kwargs)
        super().__init__(ttk.Spinbox, tk_options, parent=parent)

        # Track last emitted change text
        self._prev_change_text = self._signal()

        # Subscribe to display edits (no parse)
        self._on_input_fid = self._signal.subscribe(self._handle_change)

        # Commit on blur/enter; then emit CHANGED only if numeric value actually changed
        self.on(Event.FOCUS).listen(self._store_prev_value)
        self.on(Event.BLUR).listen(lambda _: (self.commit(), self._check_if_changed()))
        self.on(Event.RETURN).tap(lambda _: (self.commit(), self._check_if_changed())).then_stop()

        # External callbacks
        if on_input:
            self.on_input().listen(on_input)
        if on_enter:
            self.on_enter().listen(on_enter)

        if initial_focus:
            self.focus()

    # ---------------------------
    # Public API
    # ---------------------------

    def display(self, text: Optional[str] = None):
        """Get or set the raw display text. Setting does not auto-commit."""
        if text is None:
            return self._signal()
        self._signal.set(text)
        return self

    _NOARG = object()

    def value(self, value: Number | object = _NOARG):
        """
        Get or set the committed numeric value.

        - Getter: returns the last **committed** number (or None if blank).
        - Setter: updates the display text; parse/format occurs on next `commit()`.
        """
        if value is not self._NOARG:
            if value is None:
                self._signal.set("")
            else:
                self._signal.set(str(value))
            return self
        return self._value

    def commit(self) -> None:
        """
        Parse display → numeric value, clamp to [min, max], and normalize display text.
        Runs on blur/Enter (and can be called manually).
        """
        try:
            s = self.widget.get()
        except Exception:
            s = self._signal()
        s = (s or "").strip()

        # Parse once
        if s == "":
            self._value = None if self._allow_blank else self._value
        else:
            try:
                parsed = (
                    self._fmt.parse(s, self._display_format) if self._display_format is not None
                    else self._parse_plain_number(s)
                )
                self._value = self._coerce_num(parsed)
            except (ValueError, TypeError):
                # Keep prior numeric value on parse failure
                return

        # Clamp to Tk range if we have a number
        if self._value is not None:
            try:
                vmin = self.widget.cget("from")
                vmax = self.widget.cget("to")
                self._value = min(max(self._value, vmin), vmax)
            except Exception:
                pass

        # Pretty-format once
        new_text = "" if self._value is None else self._format_number(self._value)

        if new_text != self._signal():
            # Temporarily silence <<Input>> while normalizing text to avoid feedback
            fid = getattr(self, "_on_input_fid", None)
            if fid:
                try:
                    self._signal.unsubscribe(fid)
                except Exception:
                    pass
            self._signal.set(new_text)
            if fid:
                self._on_input_fid = self._signal.subscribe(self._handle_change)

    def display_format(self, spec: Optional[FormatSpec] = None):
        """
        Get or set the Intl number format spec (None = no Intl parse/format).

        Validation: when setting, we test-format a sample number to ensure the
        spec is **numeric**. Non-number specs raise ValueError.
        """
        if spec is None:
            return self._display_format
        if spec is not None:
            try:
                _ = self._fmt.format(12345.678, spec)
            except Exception as e:
                raise ValueError(f"display_format must be a *number* spec: {e}") from e
        self._display_format = spec

        # Re-normalize current display if we already have a committed value
        v = getattr(self, "_value", None)  # <-- guard against early calls
        if v is not None:
            self._signal.set(self._format_number(v))
        return self

    def allow_blank(self, flag: Optional[bool] = None):
        """Get or set whether empty display maps to None on commit."""
        if flag is None:
            return self._allow_blank
        self._allow_blank = bool(flag)
        return self

    def signal(self, value: Signal[str | int | float] = None):
        """
        Get or replace the underlying **display** Signal (StringVar-backed preferred).

        If replacing, we safely unsubscribe from the old signal and resubscribe
        to the new one, resetting the <<Input>> baseline.
        """
        if value is None:
            return self._signal

        # Unsubscribe old
        fid = getattr(self, "_on_input_fid", None)
        if fid:
            try:
                self._signal.unsubscribe(fid)
            except Exception:
                pass

        self._signal = value
        self.configure(textvariable=self._signal.var)

        # Resubscribe and reset baseline
        self._on_input_fid = self._signal.subscribe(self._handle_change)
        self._prev_change_text = self._signal()
        return self

    # ---------------------------
    # Events
    # ---------------------------

    def _store_prev_value(self, _: Any) -> None:
        self._prev_changed_value = self._value

    def _handle_change(self, _: Any) -> None:
        """
        Text-level change handler (no parse/format).
        Emits <<Input>> with `text` only, on every actual text edit.
        """
        text = self._signal()
        if text == self._prev_change_text:
            return
        self._prev_change_text = text
        self.emit(Event.INPUT, text=text)

    def _check_if_changed(self) -> None:
        """If the parsed value changed since focus-in, emit <<Changed>> with numeric value data."""
        if self._value != self._prev_changed_value:
            self.emit(
                Event.CHANGED,
                value=encode_event_value_data(self._value),
                prev_value=encode_event_value_data(self._prev_changed_value),
                text=self._signal(),  # include display for convenience
            )
            self._prev_changed_value = self._value

    def on_input(
            self,
            handler: Optional[EventHandler] = None,
            *, scope: Scope = "widget",
    ) -> Stream[SpinboxInputEvent] | Self:
        """Stream or chainable binding for <<Input>> (text-only edits)."""
        stream = self.on(Event.INPUT, scope=scope)
        if handler is None:
            return stream
        stream.listen(handler)
        return self

    def on_enter(
            self,
            handler: Optional[EventHandler] = None,
            *, scope: Scope = "widget",
    ) -> Stream[SpinboxEnterEvent] | Self:
        """Stream or chainable binding for <Return> (emits after commit)."""

        def enrich(e: Any):
            e.data.update({"value": encode_event_value_data(self._value), "text": self._signal()})
            return e

        stream = self.on(Event.RETURN, scope=scope).map(enrich)
        if handler is None:
            return stream
        stream.listen(handler)
        return self

    def on_changed(
            self,
            handler: Optional[EventHandler] = None,
            *, scope: Scope = "widget",
    ) -> Stream[SpinboxChangedEvent] | Self:
        """Stream or chainable binding for <<Changed>> (committed numeric value on blur/Enter)."""
        stream = self.on(Event.CHANGED, scope=scope)
        if handler is None:
            return stream
        stream.listen(handler)
        return self

    # ---------------------------
    # Internals / helpers / lifecycle
    # ---------------------------

    def _coerce_num(self, x: Number) -> Number:
        return float(x) if self._num_type is float else int(round(float(x)))

    def _parse_plain_number(self, s: str) -> Number:
        # Plain parse without Intl (accepts int/float strings)
        return float(s) if (self._num_type is float or any(c in s for c in ".eE")) else int(s)

    def _parse_number_or_none(self, s: str) -> Optional[Number]:
        s2 = (s or "").strip()
        if not s2:
            return None
        try:
            return (
                self._fmt.parse(s2, self._display_format) if self._display_format is not None
                else self._parse_plain_number(s2)
            )
        except Exception:
            return None

    def _format_number(self, x: Number) -> str:
        return (
            str(x) if self._display_format is None
            else self._fmt.format(float(x), self._display_format)
        )

    def destroy(self) -> None:
        """Clean up subscriptions and destroy the widget."""
        if getattr(self, "_on_input_fid", None):
            try:
                self._signal.unsubscribe(self._on_input_fid)
            except Exception:
                pass
            self._on_input_fid = None
        super().destroy()
