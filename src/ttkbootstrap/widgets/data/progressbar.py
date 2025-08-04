from typing import Any, Callable, Unpack, Literal

from tkinter import ttk
from ttkbootstrap.core.signal import Signal
from ttkbootstrap.core.libtypes import ProgressOptions, Orient
from ttkbootstrap.core.widget import BaseWidget, current_layout
from ttkbootstrap.style.builders.progress import ProgressStyleBuilder
from ttkbootstrap.style.tokens import SemanticColor
from ttkbootstrap.utils import unsnake_kwargs


class ProgressBar(BaseWidget):
    _configure_methods = {"on_change", "signal", "value", "maximum", "orient", "color", "variant"}

    def __init__(
            self,
            parent=None,
            value: int = 0,
            color: SemanticColor = "primary",
            orient: Orient = "horizontal",
            variant: Literal['default', 'striped'] = "default",
            on_change: Callable[[int], Any] = None,
            **kwargs: Unpack[ProgressOptions]):
        """
        Create a progress bar widget with signal-based value tracking and styling.

        Args:
            parent: The parent widget.
            value: The initial value of the progress bar.
            color: The semantic color for the progress bar (e.g., "primary", "success", "danger").
            orient: The orientation of the progress bar; either "horizontal" or "vertical".
            variant: The visual style variant of the progress bar, either "default" or "striped".
            on_change: Optional callback function invoked with the new value when it changes.
            **kwargs: Additional keyword arguments
        """
        parent or current_layout()
        self._style_builder = ProgressStyleBuilder(orient=orient, color=color, variant=variant)
        self._signal = Signal(value)
        self._status = 'active'
        self._on_change = on_change
        self._on_change_fid = None

        self._widget = ttk.Progressbar(parent, orient=orient, variable=self._signal.var, **unsnake_kwargs(kwargs))

        if self._on_change:
            self.on_change(self._on_change)

        super().__init__(parent)
        self.update_style()

    def orient(self, value: Orient = None):
        """Get or set the widget orientation"""
        if value is None:
            return self.configure('orient')
        else:
            self._style_builder.orient(value)
            self.configure(orient=value)
            self._style_builder.register_style()
            return self

    def color(self, value: SemanticColor = None):
        """Get or set the progressbar color"""
        if value is None:
            return self._style_builder.color()
        else:
            self._style_builder.color(value)
            self._style_builder.register_style()
            return self

    def variant(self, value: Literal['default', 'striped'] = None):
        """Get or set the progressbar variant: 'default' or 'striped'"""
        if value is None:
            return self._style_builder.variant()
        else:
            self._style_builder.orient(value)
            self._style_builder.register_style()
            return self

    def on_change(self, value: Callable[[int], Any] = None):
        """Get or set the callback triggered when the group value changes."""
        if value is None:
            return self._on_change
        if self._on_change_fid:
            self._signal.unsubscribe(self._on_change)
        self._on_change = value
        self._on_change_fid = self._signal.subscribe(self._on_change)
        return self

    def signal(self, value: Signal = None):
        """Get or set the signal controlling the slider value."""
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
            self._signal.set(value)
            return self

    def maximum(self, value: int = None):
        """Get or set the maximum value for the progress bar."""
        if value is None:
            return self.configure("maximum")
        else:
            self.configure(maximum=value)
            return self

    def start(self, interval: int = 10):
        """Start the indeterminate progress animation."""
        self.widget.start(interval)
        return self

    def stop(self):
        """Stop the indeterminate progress animation."""
        self.widget.stop()
        return self

    def step(self, value=1, clamp=True):
        """Adjust the value of the progressbar by `value` steps.

        If `clamp` is True, ensures the value does not exceed maximum.
        """
        current = self._signal()
        new = current + value
        if clamp:
            new = min(new, self.maximum())
            self._signal.set(new)
        else:
            self.widget.step(value)
        return self

    def destroy(self):
        """Unsubscribe listeners and destroy the widget."""
        if self._on_change_fid:
            self._signal.unsubscribe(self._on_change_fid)
            self._on_change_fid = None
        super().destroy()
