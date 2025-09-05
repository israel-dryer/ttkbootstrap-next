from __future__ import annotations

from tkinter import ttk
from tkinter.font import Font
from typing import Any, Callable, Optional, Unpack

from ttkbootstrap.interop.spec.types import UIEvent
from ttkbootstrap.types import Justify, Padding, CoreOptions
from ttkbootstrap.events import Event, event_handler
from ttkbootstrap.utils import assert_valid_keys, encode_event_value_data
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.widgets.mixins.entry_mixin import EntryMixin
from ttkbootstrap.widgets.mixins.validatable_mixin import ValidationMixin
from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.style.builders.entry import EntryStyleBuilder

# Intl formatter (auto-locale inside)
from ttkbootstrap.localization.intl_format import IntlFormatter, FormatSpec


class EntryOptions(CoreOptions, total=False):
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


class EntryPart(ValidationMixin, EntryMixin, BaseWidget):
    """
    Intl-aware Entry with separate display (string) vs value (parsed), using an
    INTERNAL IntlFormatter() (auto-detected locale). No external formatter required.

    Public API:
      - display([text])           -> str | self       # get/set raw entry text
      - value([obj])              -> Any | self       # get/set parsed Python value
      - commit()                  -> None             # parse display -> value, normalize display
      - display_format([spec])    -> FormatSpec | self | None
      - allow_blank([flag])       -> bool | self
      - on_value_change([cb])     -> cb | self
    """

    widget: ttk.Entry

    _configure_methods = {
        "value": "value",
        "display": "display",
        "display_format": "display_format",
        "allow_blank": "allow_blank",
        "on_value_change": "on_value_change",
        "on_enter": "on_enter",
        "on_changed": "on_changed",
        "on_change": "on_change",
        "signal": "signal",
        "readonly": "readonly",
        "commit": "commit",
    }

    def __init__(
            self,
            value: Any | Signal = "",
            *,
            display_format: Optional[FormatSpec] = None,  # None = no formatting/parsing by IntlFormatter
            allow_blank: bool = True,
            on_value_change: Callable[[UIEvent], Any] = None,  # value changes
            on_change: Callable[[UIEvent], Any] = None,  # display changes
            on_enter: Callable[[UIEvent], Any] = None,
            initial_focus: bool = False,
            **kwargs: Unpack[EntryOptions],
    ):
        self._style_builder = EntryStyleBuilder()

        # Internal Intl engine (auto-detects locale; dayfirst/yearfirst False by default)
        self._fmt = IntlFormatter()
        self._display_format = display_format
        self._allow_blank = allow_blank
        self._on_value_change_cb = on_value_change

        # Initialize display + parsed value
        if isinstance(value, Signal):
            initial_display = value()
            initial_value = self._parse_or_none(initial_display)
            self._signal = value
        elif isinstance(value, str):
            initial_display = value
            initial_value = self._parse_or_none(initial_display)
            self._signal = Signal(initial_display)
        else:
            # Treat as parsed value and format for display
            initial_value = value
            if value is None:
                initial_display = ""
            else:
                if self._display_format is None:
                    initial_display = str(value)
                else:
                    initial_display = self._fmt.format(value, self._display_format)
            self._signal = Signal(initial_display)

        self._value = initial_value
        self._prev_change_value = initial_value
        self._prev_changed_value = initial_value
        self._on_change = None
        self._on_change_fid = None

        # Normalize initial display if we already have a parsed value
        if self._value is not None:
            if self._display_format is None:
                self._signal.set(str(self._value))
            else:
                self._signal.set(self._fmt.format(self._value, self._display_format))

        parent = kwargs.pop("parent", None)
        assert_valid_keys(kwargs, EntryOptions, where="EntryPart")
        tk_options = dict(textvariable=self._signal.var, **kwargs)
        super().__init__(ttk.Entry, tk_options, parent=parent)

        # External callbacks
        if on_change:
            self.on_change(on_change)
        if on_enter:
            self.on_enter(on_enter)

        # On change event handler
        self._on_change_fid = self._signal.subscribe(self._handle_change)

        # Normalize-on-commit on blur/enter, and emit CHANGED only when parsed value differs
        self.bind(Event.FOCUS, self._store_prev_value)
        self.bind(Event.BLUR, lambda e: (self.commit(), self._check_if_changed(None)))
        self.bind(Event.RETURN, lambda e: (self.commit(), self._check_if_changed(None), "break"))

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

    def value(self, obj: Any = ...):
        """
        Get or set the parsed Python value.
        - No args → returns the parsed value (number/date/time/datetime/str/None).
        - With arg → sets the parsed value and re-renders display.
        """
        if obj is ...:
            return self._value
        self._value = obj
        if obj is None:
            disp = ""
        else:
            if self._display_format is None:
                disp = str(obj)
            else:
                disp = self._fmt.format(obj, self._display_format)
        self._signal.set(disp)
        return self

    def commit(self) -> None:
        """
        Parse current display → store as parsed value; normalize display format.
        Leaves display/value unchanged if parse fails.
        """
        s = (self._signal() or "").strip()
        if s == "":
            if self._allow_blank:
                self._value = None
            return

        try:
            if self._display_format is None:
                # No Intl parsing → raw string as the model value
                parsed = s
            else:
                parsed = self._fmt.parse(s, self._display_format)
        except ValueError:
            return  # keep user input as-is

        self._value = parsed
        # Normalize display from parsed value
        if parsed is None:
            self._signal.set("")
        else:
            if self._display_format is None:
                self._signal.set(str(parsed))
            else:
                self._signal.set(self._fmt.format(parsed, self._display_format))

    def display_format(self, spec: Optional[FormatSpec] = None):
        """
        Get or set the format spec (preset/dict/CLDR pattern).
        None means: no Intl formatting/parsing; treat model value as raw string and display str(value).
        """
        if spec is None:
            return self._display_format
        self._display_format = spec
        if self._value is not None:
            if self._display_format is None:
                self._signal.set(str(self._value))
            else:
                self._signal.set(self._fmt.format(self._value, self._display_format))
        return self

    def allow_blank(self, flag: Optional[bool] = None):
        """Get or set whether empty display maps to None on commit."""
        if flag is None:
            return self._allow_blank
        self._allow_blank = bool(flag)
        return self

    def on_value_change(self, cb: Optional[Callable[[Any], Any]] = None):
        """Get or set callback invoked when parsed value actually changes."""
        if cb is None:
            return self._on_value_change_cb
        self._on_value_change_cb = cb
        return self

    # Legacy helpers retained (display-level semantics)

    def value_text(self) -> str:
        """Return current display text (string)."""
        return self._signal()

    def signal(self, value: Signal[str | int] = None):
        """Get or set the display Signal (StringVar-backed)."""
        if value is None:
            return self._signal
        self._signal = value
        self.configure(textvariable=self._signal.var)
        return self

    # ---------------------------
    # Events
    # ---------------------------

    def _store_prev_value(self, _: Any) -> None:
        self._prev_changed_value = self._value
        self._prev_change_value = self._value

    def _handle_change(self, _: Any) -> None:
        current_text = self.display()
        new_parsed = self._parse_or_none(current_text)
        if new_parsed == self._prev_change_value:
            return
        self.emit(
            Event.CHANGE,
            data={
                "value": encode_event_value_data(new_parsed),
                "prev_value": encode_event_value_data(self._prev_change_value),
                "text": self.display()
            })
        self._prev_change_value = new_parsed

    def _check_if_changed(self, _: Any) -> None:
        if self._value != self._prev_changed_value:
            self.emit(
                Event.CHANGED,
                data={
                    "value": encode_event_value_data(self._value),
                    "prev_value": encode_event_value_data(self._prev_changed_value),
                    "text": self.display()
                })
            self._prev_changed_value = self._value

    @event_handler(Event.CHANGE)
    def on_change(self, value=None):
        """Bind or get the <<Change>> event handler"""
        ...

    def _transform_on_enter(self, event: UIEvent):
        """Transform for the on_enter handler"""
        event.data.update(
            {
                "value": encode_event_value_data(self._value),
                "text": self.display()}
        )
        return event

    @event_handler(Event.RETURN, transform="_transform_on_enter")
    def on_enter(self, value: Callable = None):
        """Bind or get the <Return> event handler"""
        ...

    @event_handler(Event.CHANGED)
    def on_changed(self, value: Callable = None):
        """Bind or get the <<Changed>> event handler"""
        ...

    # ---------------------------
    # Internals / lifecycle
    # ---------------------------

    def _parse_or_none(self, s: str) -> Any:
        s2 = (s or "").strip()
        if not s2:
            return None
        try:
            if self._display_format is None:
                # No Intl parsing: treat non-empty text as the model value
                return s2
            return self._fmt.parse(s2, self._display_format)
        except ValueError:
            return None

    def destroy(self) -> None:
        """Clean up subscriptions and destroy the widget."""
        if self._on_change_fid:
            self._signal.unsubscribe(self._on_change_fid)
            self._on_change_fid = None
        super().destroy()
