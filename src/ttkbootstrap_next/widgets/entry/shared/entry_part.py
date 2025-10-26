from __future__ import annotations

from tkinter import ttk
from typing import Any, Optional, Self, Unpack

from ttkbootstrap_next.core.base_widget import BaseWidget
from ttkbootstrap_next.events import Event
from ttkbootstrap_next.interop.runtime.binding import Stream
from ttkbootstrap_next.interop.runtime.configure import configure_delegate
from ttkbootstrap_next.localization.intl_format import FormatSpec, IntlFormatter
from ttkbootstrap_next.signals.signal import Signal
from ttkbootstrap_next.types import Variable
from ttkbootstrap_next.utils import assert_valid_keys, encode_event_value_data
from ttkbootstrap_next.widgets.entry.events import EntryChangedEvent, EntryEnterEvent, EntryInputEvent
from ttkbootstrap_next.widgets.entry.shared.entry_mixin import EntryMixin
from ttkbootstrap_next.widgets.entry.shared.validatable_mixin import ValidationMixin
from ttkbootstrap_next.widgets.entry.style import EntryStyleBuilder
from ttkbootstrap_next.widgets.entry.types import EntryOptions


class EntryPart(ValidationMixin, EntryMixin, BaseWidget):
    """
    Intl-aware Entry that cleanly separates **typed text** (`display`) from the
    **committed/parsed value** (`value`). Parsing/formatting happens only on commit
    (blur or Enter), keeping typing snappy.
    """

    widget: ttk.Entry

    def __init__(
            self,
            value: Any | Signal = "",
            *,
            value_format: Optional[FormatSpec] = None,
            allow_blank: bool = True,
            initial_focus: bool = False,
            **kwargs: Unpack[EntryOptions],
    ):
        """Create an Entry with decoupled text vs value semantics."""
        self._style_builder = EntryStyleBuilder()

        # Intl engine (allow per-widget locale)
        locale_arg = kwargs.pop("locale", None)
        self._fmt = IntlFormatter(locale=locale_arg)
        self._value_format = value_format
        self._allow_blank = allow_blank

        # Initialize display + parsed value
        if isinstance(value, Signal):
            initial_display = value()
            initial_value = self._parse_or_none(initial_display) if value_format is not None else (
                    initial_display or None
            )
            self._signal = value
        elif isinstance(value, str):
            initial_display = value
            initial_value = self._parse_or_none(initial_display) if value_format is not None else (
                    initial_display or None
            )
            self._signal = Signal(initial_display)
        else:
            # Treat as parsed value and format for display
            initial_value = value
            if value is None:
                initial_display = ""
            else:
                initial_display = (
                    str(value) if self._value_format is None else self._fmt.format(value, self._value_format)
                )
            self._signal = Signal(initial_display)

        self._value = initial_value
        self._prev_changed_value = initial_value

        # Normalize initial display if we already have a parsed value
        if self._value is not None:
            self._signal.set(
                str(self._value) if self._value_format is None else self._fmt.format(
                    self._value, self._value_format)
            )

        parent = kwargs.pop("parent", None)
        # `locale` is consumed above and must not be passed to Tk
        assert_valid_keys(kwargs, EntryOptions, where="EntryPart")
        tk_options = dict(textvariable=self._signal.var, **kwargs)
        super().__init__(ttk.Entry, tk_options, parent=parent)

        # Track last text we emitted for CHANGE
        self._prev_change_text = self._signal()

        # Subscribe to text changes (no debounce, no parse)
        self._on_input_fid = self._signal.subscribe(self._handle_change)

        # Commit on blur/enter; emit CHANGED only when the parsed value actually differs
        self.on(Event.FOCUS).listen(self._store_prev_value)
        self.on(Event.BLUR).listen(lambda _: (self.commit(), self._check_if_changed()))
        self.on(Event.RETURN).tap(lambda _: (self.commit(), self._check_if_changed())).then_stop()

        if initial_focus:
            self.focus()

    _NOARG = object()

    # ---------------------------
    # Public API
    # ---------------------------

    def signal(self):
        """The signal bound to the widget value"""
        return self._signal

    def text(self, text: Optional[str] = None):
        """Get or set the raw display text. Setting does not auto-commit."""
        if text is None:
            return self._signal()
        self._signal.set(text)
        return self

    def destroy(self) -> None:
        """Clean up subscriptions and destroy the widget."""
        if getattr(self, "_on_input_fid", None):
            try:
                self._signal.unsubscribe(self._on_input_fid)
            except Exception:
                pass
            self._on_input_fid = None
        super().destroy()

    def value(self, value: Any = _NOARG):
        """
        Get or set the parsed value.

        - Getter: returns the *last committed* value (no live parsing).
        - Setter: sets display text; parsing/formatting occurs on next `commit()`.
        """
        if value is not self._NOARG:
            if value is None:
                self._signal.set("")
            else:
                # Keep setter cheap; pretty-print on commit.
                self._signal.set(str(value))
            return self
        return self._value

    def commit(self) -> None:
        """Parse display → model and normalize the display text (runs on blur/Enter)."""
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
                self._value = s if self._value_format is None else self._fmt.parse(s, self._value_format)
            except ValueError:
                # Keep prior value on parse failure
                return

        # Pretty-format once
        if self._value is None:
            new_text = ""
        else:
            new_text = str(self._value) if self._value_format is None else self._fmt.format(
                self._value, self._value_format)

        if new_text != self._signal():
            # Temporarily silence CHANGE while normalizing text
            fid = getattr(self, "_on_input_fid", None)
            if fid:
                try:
                    self._signal.unsubscribe(fid)
                except Exception:
                    pass
            self._signal.set(new_text)
            if fid:
                self._on_input_fid = self._signal.subscribe(self._handle_change)

    # ---- Configuration delegates -----

    @configure_delegate("readonly")
    def readonly(self, value: bool = None):
        """Get or set readonly state."""
        if value is None:
            return "readonly" in self.widget.state()
        states = ['disabled', 'readonly'] if value else ['!disabled', '!readonly']
        self.widget.state(states)
        return self

    @configure_delegate("value_format")
    def _configure_value_format(self, spec: Optional[FormatSpec] = None):
        """Get or set the Intl format spec (None = no Intl parsing/formatting)."""
        if spec is None:
            return self._value_format
        self._value_format = spec
        if self._value is not None:
            self._signal.set(
                str(self._value) if self._value_format is None else self._fmt.format(
                    self._value, self._value_format)
            )
        return self

    @configure_delegate("allow_blank")
    def _configure_allow_blank(self, flag: Optional[bool] = None):
        """Get or set whether empty display maps to None on commit."""
        if flag is None:
            return self._allow_blank
        self._allow_blank = bool(flag)
        return self

    @configure_delegate("signal")
    def _configure_signal(self, value: Signal[str | int] = None):
        """Get or replace the underlying display Signal (StringVar-backed)."""
        if value is None:
            return self._signal

        # Unsubscribe from old signal to avoid duplicate callbacks
        fid = getattr(self, "_on_input_fid", None)
        if fid:
            try:
                self._signal.unsubscribe(fid)
            except Exception:
                pass

        self._signal = value
        self.configure(textvariable=self._signal.var)

        # Resubscribe and reset CHANGE baseline
        self._on_input_fid = self._signal.subscribe(self._handle_change)
        self._prev_change_text = self._signal()
        return self

    @configure_delegate("text_variable")
    @configure_delegate("textvariable")
    def _configure_text_variable(self, value: Variable = None):
        if value is None:
            return self._signal
        else:
            return self._configure_signal(Signal.from_variable(value))

    # ---- Event handlers -----

    def _store_prev_value(self, _: Any) -> None:
        self._prev_changed_value = self._value

    def _handle_change(self, _: Any) -> None:
        """
        Text-level change handler (no parse/format).
        Emits <<Change>> with `text` only, on every actual text edit.
        """
        text = self._signal()
        if text == self._prev_change_text:
            return
        self._prev_change_text = text
        # IMPORTANT: no value data here, by design.
        self.emit(Event.INPUT, text=text)

    def _check_if_changed(self) -> None:
        """If the parsed value changed since focus-in, emit <<Changed>> with value data."""
        if self._value != self._prev_changed_value:
            self.emit(
                Event.CHANGED,
                value=encode_event_value_data(self._value),
                prev_value=encode_event_value_data(self._prev_changed_value),
                text=self._signal(),  # include display for convenience
            )
            self._prev_changed_value = self._value

    def on_input(self) -> Stream[EntryInputEvent] | Self:
        """Convenience alias for input stream"""
        return self.on(Event.INPUT)

    def on_enter(self) -> Stream[EntryEnterEvent]:
        """Convenience alias for enter stream"""

        def enrich(e: Any):
            e.data.update({"value": encode_event_value_data(self._value), "text": self._signal()})
            return e

        return self.on(Event.RETURN).map(enrich)

    def on_changed(self) -> Stream[EntryChangedEvent]:
        """Convenience alias for changed stream"""
        return self.on(Event.CHANGED)

    # ---- Internals lifecycle -----

    def _parse_or_none(self, s: str) -> Any:
        s2 = (s or "").strip()
        if not s2:
            return None
        try:
            if self._value_format is None:
                return s2
            return self._fmt.parse(s2, self._value_format)
        except ValueError:
            return None
