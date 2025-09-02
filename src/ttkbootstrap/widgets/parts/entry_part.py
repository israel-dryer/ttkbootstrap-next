from tkinter import ttk
from tkinter.font import Font
from typing import Any, Callable, TypedDict, Unpack

from ttkbootstrap.types import Justify, Padding, Widget
from ttkbootstrap.events import Event, event_handler
from ttkbootstrap.utils import assert_valid_keys
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.widgets.mixins.entry_mixin import EntryMixin
from ttkbootstrap.widgets.mixins.validatable_mixin import ValidationMixin
from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.style.builders.entry import EntryStyleBuilder


class EntryOptions(TypedDict, total=False):
    """
    Options for configuring an entry widget.

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
    parent: Widget


class EntryPart(ValidationMixin, EntryMixin, BaseWidget):
    widget: ttk.Entry

    _configure_methods = {
        "value": "value",
        "on_enter": "on_enter",
        "on_changed": "on_changed",
        "on_change": "on_change",
        "signal": "signal",
        "readonly": "readonly"
    }

    def __init__(
            self,
            value: str | Signal = "",
            *,
            on_change: Callable[[str], Any] = None,
            on_enter: Callable[[str], Any] = None,
            on_changed: Callable[[str], Any] = None,
            initial_focus: bool = False,
            **kwargs: Unpack[EntryOptions]
    ):
        """
        A base class for Entry widgets with signal binding and validation.

        Args:
            value: Initial value of the entry.
            on_change: Callback triggered when the signal value changes.
            on_enter: Callback triggered when Enter is pressed.
            on_changed: Callback triggered when the entry loses focus and value changed.
            initial_focus: Whether to give the entry focus after creation.
            **kwargs: Additional entry options.
        """
        self._on_change = None
        self._on_change_fid = None
        self._on_enter = None
        self._on_changed = None
        self._style_builder = EntryStyleBuilder()
        self._signal = value if isinstance(value, Signal) else Signal(value)
        self._prev_value = value

        parent = kwargs.pop('parent', None)

        assert_valid_keys(kwargs, EntryOptions, where="EntryPart")
        tk_options = dict(textvariable=self._signal.var, **kwargs)
        super().__init__(ttk.Entry, tk_options, parent=parent)

        if on_change:
            self.on_change(on_change)
        if on_enter:
            self.on_enter(on_enter)
        if on_changed:
            self.on_changed(on_changed)

        self.bind(Event.FOCUS, self._store_prev_value)
        self.bind(Event.BLUR, self._check_if_changed)

        if initial_focus:
            self.focus()

    def _store_prev_value(self, _: Any) -> None:
        """Save the current value before focus in."""
        self._prev_value = self._signal()

    def _check_if_changed(self, _: Any) -> None:
        """Compare current value with previous and fire 'changed' event if different."""
        if self._signal() != self._prev_value:
            self.emit(Event.CHANGED)

    def value(self, value: str = None):
        """Get or set the entry value."""
        if value is None:
            return self._signal()
        self._signal.set(value)
        return self

    def signal(self, value: Signal[str | int] = None):
        """Get or set the signal."""
        if value is None:
            return self._signal
        self._signal = value
        self.configure(textvariable=self._signal.var)
        return self

    def on_change(self, value: Callable[[Any], Any] = None):
        """Set callback for when the signal value changes."""
        if value is None:
            return self._on_change
        if self._on_change_fid:
            self._signal.unsubscribe(self._on_change)
        self._on_change = value
        self._on_change_fid = self._signal.subscribe(self._on_change)
        return self

    @event_handler(Event.RETURN)
    def on_enter(self, handler: Callable = None):
        """Bind or get the <Return> event handler."""
        return self._signal()

    @event_handler(Event.CHANGED)
    def on_changed(self, handler: Callable = None):
        """Set callback for when focus out causes value change."""
        return self._signal()

    def destroy(self) -> None:
        """Clean up subscriptions and destroy the widget."""
        if self._on_change_fid:
            self._signal.unsubscribe(self._on_change_fid)
            self._on_change_fid = None
        super().destroy()
