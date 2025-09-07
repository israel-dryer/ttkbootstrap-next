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
    Intl-aware Entry that cleanly separates **typed text** (`display`) from the
    **committed/parsed value** (`value`). Parsing/formatting happens only on commit
    (blur or Enter), keeping typing snappy.
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
            display_format: Optional[FormatSpec] = None,  # None ⇒ no Intl parse/format
            allow_blank: bool = True,
            on_input: EventHandler = None,  # fires with text only (every edit)
            on_enter: EventHandler = None,
            initial_focus: bool = False,
            **kwargs: Unpack[EntryOptions],
    ):
        """
        Create an Entry with decoupled text vs value semantics.

        - `display_format`: Intl format spec for parsing/formatting (date/number, etc.).
        - `allow_blank`: if True, empty text commits to `None`.
        - `on_input`: subscribe to text-level edits (no parse).
        - `on_enter`: callback for Return key (after commit).
        """
        self._style_builder = EntryStyleBuilder()

        # Intl engine (auto-detects locale)
        self._fmt = IntlFormatter()
        self._display_format = display_format
        self._allow_blank = allow_blank

        # Initialize display + parsed value
        if isinstance(value, Signal):
            initial_display = value()
            initial_value = self._parse_or_none(initial_display) if display_format is not None else (
                    initial_display or None
            )
            self._signal = value
        elif isinstance(value, str):
            initial_display = value
            initial_value = self._parse_or_none(initial_display) if display_format is not None else (
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
                    str(value) if self._display_format is None else self._fmt.format(value, self._display_format)
                )
            self._signal = Signal(initial_display)

        self._value = initial_value
        self._prev_changed_value = initial_value

        # Normalize initial display if we already have a parsed value
        if self._value is not None:
            self._signal.set(
                str(self._value) if self._display_format is None else self._fmt.format(
                    self._value, self._display_format)
            )

        parent = kwargs.pop("parent", None)
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
                self._value = s if self._display_format is None else self._fmt.parse(s, self._display_format)
            except ValueError:
                # Keep prior value on parse failure
                return

        # Pretty-format once
        if self._value is None:
            new_text = ""
        else:
            new_text = str(self._value) if self._display_format is None else self._fmt.format(
                self._value, self._display_format)

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

    def display_format(self, spec: Optional[FormatSpec] = None):
        """Get or set the Intl format spec (None = no Intl parsing/formatting)."""
        if spec is None:
            return self._display_format
        self._display_format = spec
        if self._value is not None:
            self._signal.set(
                str(self._value) if self._display_format is None else self._fmt.format(
                    self._value, self._display_format)
            )
        return self

    def allow_blank(self, flag: Optional[bool] = None):
        """Get or set whether empty display maps to None on commit."""
        if flag is None:
            return self._allow_blank
        self._allow_blank = bool(flag)
        return self

    # Legacy helpers (display-level semantics)
    def value_text(self) -> str:
        """Return current display text (string)."""
        return self._signal()

    def signal(self, value: Signal[str | int] = None):
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

    # ---------------------------
    # Events
    # ---------------------------

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

    def on_input(
            self,
            handler: Optional[EventHandler] = None,
            *, scope: Scope = "widget",
    ) -> Stream[Any] | Self:
        """Stream or chainable binding for <<Change>> (text-only)."""
        stream = self.on(Event.INPUT, scope=scope)
        if handler is None:
            return stream
        stream.listen(handler)
        return self

    def on_enter(
            self,
            handler: Optional[EventHandler] = None,
            *, scope: Scope = "widget",
    ) -> Stream[Any] | Self:
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
    ) -> Stream | Self:
        """Stream or chainable binding for <<Changed>> (committed value on blur/Enter)."""
        stream = self.on(Event.CHANGED, scope=scope)
        if handler is None:
            return stream
        stream.listen(handler)
        return self

    # ---------------------------
    # Internals / lifecycle
    # ---------------------------

    def _parse_or_none(self, s: str) -> Any:
        s2 = (s or "").strip()
        if not s2:
            return None
        try:
            if self._display_format is None:
                return s2
            return self._fmt.parse(s2, self._display_format)
        except ValueError:
            return None

    def destroy(self) -> None:
        """Clean up subscriptions and destroy the widget."""
        if getattr(self, "_on_input_fid", None):
            try:
                self._signal.unsubscribe(self._on_input_fid)
            except Exception:
                pass
            self._on_input_fid = None
        super().destroy()
