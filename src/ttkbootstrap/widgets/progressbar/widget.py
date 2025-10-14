from tkinter import ttk
from typing import Literal, Unpack

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.events import Event
from ttkbootstrap.interop.runtime.binding import Stream
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.style.types import SemanticColor
from ttkbootstrap.types import Orientation
from ttkbootstrap.widgets.progressbar.events import ProgressbarChangedEvent, ProgressbarCompleteEvent
from ttkbootstrap.widgets.progressbar.style import ProgressbarStyleBuilder
from ttkbootstrap.widgets.progressbar.types import ProgressbarOptions


class Progressbar(BaseWidget):
    widget: ttk.Progressbar
    _configure_methods = {
        "orient": "_configure_orient",
        "color": "_configure_color",
        "variant": "_configure_variant",
        "signal": "_configure_signal",
    }

    def __init__(
            self,
            value: float | Signal = 0.0,
            *,
            color: SemanticColor = "primary",
            orient: Orientation = "horizontal",
            variant: Literal['default', 'striped'] = "default",
            **kwargs: Unpack[ProgressbarOptions]):
        """
        Create a progress bar widget with signal-based value tracking and styling.

        Args:
            value: The initial value of the progress bar.

        Keyword Args:
            color: The semantic color for the progress bar (e.g., "primary", "success", "danger").
            cursor: The cursor that appears when the mouse is over the widget.
            id: A unique identifier used to query this widget.
            length: The length of the progress bar in pixels.
            maximum: The maximum value for the progress bar range.
            mode: Use 'determinate' for measurable progress and 'indeterminate' for continuous animation.
            orient: The orientation of the progress bar; either "horizontal" or "vertical".
            parent: The parent container of this widget.
            take_focus: Indicates whether the widget accepts focus during keyboard traversal.
            variable: The tkinter variable linked to this widget's value.
            variant: The visual style variant of the progress bar, either "default" or "striped".
        """
        self._style_builder = ProgressbarStyleBuilder(orient=orient, color=color, variant=variant)
        self._signal = value if isinstance(value, Signal) else Signal(float(value))
        self._prev_value = self._signal()
        self._status = 'active'

        self._on_changed_fid = None
        self._completed = False  # one-shot gate for <<Complete>>

        parent = kwargs.pop("parent", None)
        tk_options = dict(
            orient=orient,
            variable=self._signal.var,
            **kwargs
        )
        super().__init__(ttk.Progressbar, tk_options, parent=parent)
        self._on_changed_fid = self._signal.subscribe(self._handle_changed)

    def signal(self):
        """The signal bound to the widget value"""
        return self._signal

    def value(self, value: int | float = None):
        """Get or set the current progress value."""
        if value is None:
            return self._signal()
        max_value = float(self.widget.cget("maximum"))
        # clamp to avoid overshoot spam
        self._signal.set(min(float(value), max_value))
        return self

    def start(self, interval: int = 10):
        """Start the indeterminate progress animation."""
        self.widget.start(interval)
        return self

    def stop(self):
        """Stop the indeterminate progress animation."""
        self.widget.stop()
        return self

    def step(self, value=1.0, clamp=True):
        """Adjust the value by `value` steps."""
        cur = float(self._signal())
        nxt = cur + float(value)
        if clamp:
            nxt = min(nxt, float(self.widget.cget("maximum")))
            self._signal.set(nxt)
        else:
            self.widget.step(value)
        return self

    def destroy(self):
        """Unsubscribe listeners and destroy the widget."""
        if self._on_changed_fid:
            self._signal.unsubscribe(self._on_changed_fid)
            self._on_changed_fid = None
        super().destroy()

    # ---- Configuration delegates -----

    def _configure_orient(self, value: Orientation = None):
        """Get or set the widget orientation"""
        if value is None:
            return self.configure('orient')
        else:
            self._style_builder.options(orient=value)
            self.configure(orient=value)
            self._style_builder.build()
            return self

    def _configure_color(self, value: SemanticColor = None):
        """Get or set the progressbar color"""
        if value is None:
            return self._style_builder.options('color')
        else:
            self._style_builder.options(color=value)
            self._style_builder.build()
            return self

    def _configure_variant(self, value: Literal['default', 'striped'] = None):
        """Get or set the progressbar variant: 'default' or 'striped'"""
        if value is None:
            return self._style_builder.options("variant")
        else:
            self._style_builder.options(variant=value)
            self._style_builder.build()
            return self

    def _configure_signal(self, value: Signal = None):
        """Get or set the signal controlling the progress value."""
        if value is None:
            return self._signal
        if self._on_changed_fid:
            self._signal.unsubscribe(self._on_changed_fid)
        self._signal = value
        self.configure(variable=value.var)
        self._on_changed_fid = self._signal.subscribe(self._handle_changed)
        return self

    # ---- Event handlers -----

    def _handle_changed(self, *_):
        cur = float(self._signal())
        maximum = float(self.widget.cget("maximum"))
        prev = float(self._prev_value)

        # clamp
        if cur > maximum:
            cur = maximum
            self._signal.set(cur)

        if cur != prev:
            self.emit(Event.CHANGED, value=cur, prev_value=prev, when="tail")

        # one-shot COMPLETE when crossing the boundary
        if not self._completed and prev < maximum <= cur:
            self._completed = True
            self.emit(Event.COMPLETE, when="tail")

        # reset the gate if we drop below max (e.g., you reset the bar)
        if self._completed and cur < maximum:
            self._completed = False

        self._prev_value = cur

    def on_changed(self) -> Stream[ProgressbarChangedEvent]:
        """Convenience alias for the changed stream"""
        return self.on(Event.CHANGED)

    def on_complete(self) -> Stream[ProgressbarCompleteEvent]:
        """Convenience alias for the complete stream"""
        return self.on(Event.COMPLETE)


ProgressBar = Progressbar
