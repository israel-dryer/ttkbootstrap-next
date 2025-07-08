from typing import Any, Callable

from tkinter import ttk
from ttkbootstrap.core import Signal
from ttkbootstrap.core.libtypes import Orient
from ttkbootstrap.core.widget import BaseWidget
from ttkbootstrap.style.builders.progress import ProgressStyleBuilder
from ttkbootstrap.utils import unsnake_kwargs


class Progress(BaseWidget):
    _configure_methods = {}

    def __init__(
            self,
            parent,
            value: int = 0,
            orient: Orient = "horizontal",
            on_change: Callable[[int], Any] = None,
            **kwargs):
        self._style_builder = ProgressStyleBuilder()
        self._signal = Signal(value)
        self._status = 'active'
        self._on_change = on_change
        self._on_change_fid = None

        self._widget = ttk.Progressbar(parent, variable=self._signal.var, **unsnake_kwargs(kwargs))

        if self._on_change:
            self.on_change(self._on_change)

        super().__init__(parent)

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
