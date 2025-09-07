from __future__ import annotations

from tkinter import ttk
from tkinter.font import Font
from typing import Any, Callable, Optional, Self, Unpack

from ttkbootstrap.interop.runtime.binding import Scope, Stream
from ttkbootstrap.types import EventHandler, Justify, Padding, CoreOptions
from ttkbootstrap.events import Event
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
      - value([obj])              -> Any | self       # get/set parsed Python value (setter updates display; parsing occurs on commit)
      - commit()                  -> None             # parse display -> value, normalize display
      - display_format([spec])    -> FormatSpec | self | None
      - allow_blank([flag])       -> bool | self
      - on_change([cb])           -> stream/self      # text-level (per keystroke), no parse/format
      - on_changed([cb])          -> stream/self      # value-level (post-commit), parsed & normalized
    """

    widget: ttk.Entry

    _configure_methods = {
        "value": "value",
        "display": "display",
        "display_format": "display_format",
        "allow_blank": "allow_blank",
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
            on_change: EventHandler = None,  # display (text) changes – no parse
            on_enter: EventHandler = None,
            initial_focus: bool = False,
            **kwargs: Unpack[EntryOptions],
    ):
        self._style_builder = EntryStyleBuilder()
        self._dirty_text = False

        # Internal Intl engine (auto-detects locale; dayfirst/yearfirst False by default)
        self._fmt = IntlFormatter()
        self._display_format = display_format
        self._allow_blank = allow_blank

        # Initialize display + parsed value
        if isinstance(value, Signal):
            initial_display = value()
            initial_value = self._parse_or_none(initial_display) if display_format is not None else (
                        initial_display or None)
            self._signal = value
        elif isinstance(value, str):
            initial_display = value
            initial_value = self._parse_or_none(initial_display) if display_format is not None else (
                        initial_display or None)
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
        self._prev_changed_value = initial_value

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

        # text-only change tracking (featherweight hot path)
        self._prev_change_text = self._signal()
        self._change_task: str | None = None
        self._change_seq: int = 0  # guard to drop stale scheduled callbacks

        # On change event handler (subscribe after widget created/configured)
        self._on_change_fid = self._signal.subscribe(self._handle_change)

        # Normalize-on-commit on blur/enter, and emit CHANGED only when parsed value differs
        def _do_blur(_: Any):
            self.commit()
            self._check_if_changed(None)

        def _do_return(_: Any):
            self.commit()
            self._check_if_changed(None)

        self.on(Event.FOCUS).listen(self._store_prev_value)
        self.on(Event.BLUR).listen(_do_blur)
        self.on(Event.RETURN).tap(_do_return).then_stop()

        # External callbacks
        if on_change:
            self.on_change().listen(on_change)
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

    def value(self, value: Any = _NOARG):
        """
        Get or set the parsed Python value.

        - Getter (no argument): returns the *last committed* value quickly, without
          attempting to re-parse while the user is typing.
        - Setter (argument provided): updates display; parsing/normalization happens
          on the next `commit()`.
        """
        if value is not self._NOARG:
            if value is None:
                self._signal.set("")
            else:
                # Do not format here; keep setter cheap. commit() will pretty-print.
                self._signal.set(str(value))
            return self

        # During typing, avoid expensive live parse; return the committed value.
        return self._value

    def commit(self) -> None:
        """Parse from display -> model and normalize the display text (heavy work happens here)."""
        # read fresh text once
        try:
            s = self.widget.get()
        except Exception:
            s = self._signal()
        s = (s or "").strip()

        # parse once (heavy)
        if s == "":
            self._value = None if self._allow_blank else self._value
        else:
            try:
                self._value = (s if self._display_format is None
                               else self._fmt.parse(s, self._display_format))
            except ValueError:
                # keep prior value on parse failure
                return

        # pretty format once (heavy)
        if self._value is None:
            new_text = ""
        else:
            new_text = (str(self._value) if self._display_format is None
                        else self._fmt.format(self._value, self._display_format))

        # update display without creating a change storm
        if new_text != self._signal():
            fid = getattr(self, "_on_change_fid", None)
            if fid:
                try:
                    self._signal.unsubscribe(fid)
                except Exception:
                    pass

            self._signal.set(new_text)

            if fid:
                self._on_change_fid = self._signal.subscribe(self._handle_change)

        self._dirty_text = False

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

    # Legacy helpers retained (display-level semantics)
    def value_text(self) -> str:
        """Return current display text (string)."""
        return self._signal()

    def signal(self, value: Signal[str | int] = None):
        """Get or set the display Signal (StringVar-backed)."""
        if value is None:
            return self._signal

        # Unsubscribe from the old signal first to avoid duplicate callbacks
        fid = getattr(self, "_on_change_fid", None)
        if fid:
            try:
                self._signal.unsubscribe(fid)
            except Exception:
                pass

        self._signal = value
        self.configure(textvariable=self._signal.var)

        # Resubscribe to the new signal
        self._on_change_fid = self._signal.subscribe(self._handle_change)
        # Reset text-tracking baseline for CHANGE
        self._prev_change_text = self._signal()
        return self

    # ---------------------------
    # Events
    # ---------------------------

    def _store_prev_value(self, _: Any) -> None:
        self._prev_changed_value = self._value

    def _handle_change(self, _: Any) -> None:
        """Featherweight: track text changes only; no parse/format here."""
        self._dirty_text = True
        text = self._signal()  # StringVar is already current

        if text == self._prev_change_text:
            return
        self._prev_change_text = text

        # bump sequence and cancel any already-scheduled task
        self._change_seq += 1
        seq = self._change_seq
        if self._change_task:
            self.schedule_cancel(self._change_task)

        # schedule for next loop tick; stale tasks are ignored via seq guard
        self._change_task = self.schedule(0, lambda: self._emit_change_if_current(seq, text))

    def _emit_change_if_current(self, seq: int, text: str) -> None:
        """Run only for the newest scheduled change (drops stale callbacks)."""
        if seq != self._change_seq:
            return
        self._change_task = None
        # IMPORTANT: value fields are None here; consumers treat this as "text edit"
        self.emit(Event.CHANGE, value=None, prev_value=None, text=text)

    def _check_if_changed(self, _: Any) -> None:
        if self._value != self._prev_changed_value:
            self.emit(
                Event.CHANGED,
                value=encode_event_value_data(self._value),
                prev_value=encode_event_value_data(self._prev_changed_value),
                text=self._signal()
            )
            self._prev_changed_value = self._value

    def on_change(
            self,
            handler: Optional[EventHandler] = None,
            *, scope: Scope = "widget") -> Stream[Any] | Self:
        """Stream or chainable binding for <<Change>> (text-only).

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """
        stream = self.on(Event.CHANGE, scope=scope)
        if handler is None:
            return stream
        stream.listen(handler)
        return self

    def on_enter(
            self,
            handler: Optional[EventHandler] = None,
            *, scope: Scope = "widget") -> Stream[Any] | Self:
        """Stream or chainable binding for <Return>.

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """

        def update(e: Any):
            """Update event data with value and text"""
            e.data.update(
                {
                    "value": encode_event_value_data(self._value),
                    "text": self._signal()
                })
            return e

        stream = self.on(Event.RETURN, scope=scope).map(update)
        if handler is None:
            return stream
        stream.listen(handler)
        return self

    def on_changed(
            self, handler: Optional[EventHandler] = None,
            *, scope: Scope = "widget") -> Stream | Self:
        """Stream or chainable binding for <<Changed>> (committed value).

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """
        stream = self.on(Event.CHANGED, scope=scope)
        if handler is None:
            return stream
        stream.listen(handler)
        return self

    # ---------------------------
    # Internals / lifecycle
    # ---------------------------

    def _current_text(self) -> str:
        # Prefer the live widget text (freshest); fall back to your model/signal.
        try:
            return self.widget.get()
        except Exception:
            return self._signal()

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
        if getattr(self, "_on_change_fid", None):
            try:
                self._signal.unsubscribe(self._on_change_fid)
            except Exception:
                pass
            self._on_change_fid = None
        super().destroy()
