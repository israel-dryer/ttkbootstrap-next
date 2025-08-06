from typing import Any, Callable, Unpack

from tkinter import ttk
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.common.types import EntryOptions
from ttkbootstrap.widgets.mixins.validatable_mixin import ValidatableMixin
from ttkbootstrap.core.base_widget import BaseWidget, current_layout
from ttkbootstrap.style.builders.spinbox import SpinBoxStyleBuilder
from ttkbootstrap.common.utils import unsnake_kwargs


class NumberSpinboxPart(BaseWidget, ValidatableMixin):
    """A numeric spinbox widget with signal binding and validation support.

    This widget wraps a `ttk.Spinbox` and binds it to a reactive `Signal`,
    supporting live value updates, focus-based change detection, and validation hooks.

    Args:
        parent: The parent widget.
        value: Initial numeric value (default is 0).
        on_change: Callback triggered on every value change (live).
        on_enter: Callback triggered when Enter is pressed.
        on_changed: Callback triggered when value changes on focus out.
        min_value: Minimum value of the spinbox (default is 0).
        max_value: Maximum value of the spinbox (default is 100).
        increment: Step size for value changes (default is 1).
        formatter: Optional format string for display (e.g., "%.1f").
        wrap: Whether the value should wrap at min/max (default is False).
        initial_focus: Whether the widget receives focus initially.
        **kwargs: Additional keyword arguments passed to `ttk.Spinbox`.
    """

    _configure_methods = {"value", "on_change", "on_enter", "on_changed", "formatter", "signal", "readonly"}

    def __init__(
            self,
            parent=None,
            value: int | float = 0,
            on_change: Callable[[Any], int | float] = None,
            on_enter: Callable[[Any], int | float] = None,
            on_changed: Callable[[Any], int | float] = None,
            min_value: int | float = 0,
            max_value: int | float = 100,
            increment: int | float = 1,
            formatter: str = None,
            wrap: bool = False,
            initial_focus: bool = False,
            **kwargs: Unpack[EntryOptions],
    ):
        parent = parent or current_layout()
        self._on_enter = None
        self._on_change = None
        self._on_changed = None
        self._on_change_fid = None

        self._style_builder = SpinBoxStyleBuilder()
        self._signal = Signal(value)
        self._prev_value = value

        kwargs.setdefault("from", min_value)
        kwargs.setdefault("to", max_value)
        kwargs.setdefault("increment", increment)
        kwargs.setdefault("wrap", str(wrap).lower())
        if formatter:
            try:
                _ = formatter % float(value)
            except Exception:
                raise ValueError(f"Invalid format: {formatter!r}")
            kwargs["format"] = formatter

        self._widget = ttk.Spinbox(
            parent,
            textvariable=self._signal.var,
            **unsnake_kwargs(kwargs)
        )
        super().__init__(parent)
        ValidatableMixin.__init__(self)

        if on_change:
            self.on_change(on_change)

        if on_enter:
            self.on_enter(on_enter)

        if on_changed:
            self.on_changed(on_changed)

        self.bind("focus", self._store_prev_value)
        self.bind("blur", self._check_if_changed)
        self._setup_validation_events()

        if initial_focus:
            self.focus()

    def _store_prev_value(self, _: Any):
        """Store the current value before focus out."""

        self._prev_value = self._signal()

    def _check_if_changed(self, _: Any):
        """Emit the 'changed' event if the value was modified after focus out."""

        try:
            current = self._signal()
            if self._prev_value is not None and current != self._prev_value:
                self.emit("changed")
        except (ValueError, TypeError):
            pass

    def value(self, value: int | float = None):
        """Get or set the current value of the spinbox.

        Args:
            value: Optional value to set.

        Returns:
            The current value if `value` is None, otherwise self.
        """
        if value is None:
            return self._signal()
        self._signal.set(value)
        return self

    def signal(self, value: Signal[int | float] = None):
        """Get or set the bound signal.

        Args:
            value: Optional signal to assign.

        Returns:
            The current signal if `value` is None, otherwise self.
        """
        if value is None:
            return self._signal
        self._signal = value
        self.configure(textvariable=self._signal.var)
        return self

    def on_change(self, value: Callable[[int | float], Any] = None):
        """Set callback for live value changes.

        Args:
            value: A function called when the signal updates.

        Returns:
            The assigned callback or self.
        """
        if value is None:
            return self._on_change
        else:
            self._on_change = value
            self._on_change_fid = self._signal.subscribe(lambda _: self._on_change(self._signal()))
            return self

    def on_enter(self, value: Callable[[Any], Any] = None):
        """Set callback for Enter key press.

        Args:
            value: A function called when Enter is pressed.

        Returns:
            The assigned callback or self.
        """
        if value is None:
            return self._on_enter
        self._on_enter = value
        self.bind("return", lambda _: self._on_enter(self._signal()))
        return self

    def on_changed(self, value: Callable[[int], Any] = None):
        """Set callback for value changes on focus out.

        Args:
            value: A function called if the value has changed on blur.

        Returns:
            The assigned callback or self.
        """
        if value is None:
            return self._on_changed
        self._on_changed = value
        self.bind("changed", lambda e: self._on_changed(self._signal()))
        return self

    def readonly(self, value: bool = None):
        """Get or set readonly state.

        Args:
            value: If True, sets to readonly. If False, makes editable.

        Returns:
            The readonly state if `value` is None, otherwise self.
        """
        if value is None:
            return "readonly" in self.widget.state()
        states = ['disabled', 'readonly'] if value else ['!disabled', '!readonly']
        self.widget.state(states)
        return self

    def disable(self):
        """Disable the widget and make it non-editable.

        Returns:
            self
        """
        self.widget.state(['disabled'])
        return self

    def enable(self):
        """Enable the widget for editing.

        Returns:
            self
        """
        self.state(['!disabled', '!readonly'])
        return self

    def destroy(self) -> None:
        """Unsubscribe from signal and destroy the widget."""
        if self._on_change_fid:
            self._signal.unsubscribe(self._on_change_fid)
            self._on_change_fid = None
        super().destroy()

    def get_bounding_box(self, index: int) -> tuple[int, int, int, int] | None:
        """Get the bounding box of a character at a given index.

        Args:
            index: The character index.

        Returns:
            A tuple of (x, y, width, height) or None.
        """
        return self.widget.bbox(index)
