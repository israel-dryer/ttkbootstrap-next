from tkinter import ttk
from typing import Unpack

from ttkbootstrap.core import Signal
from ttkbootstrap.core.libtypes import LabelOptions
from ttkbootstrap.core.widget import BaseWidget
from ttkbootstrap.style.builders.label import LabelStyleBuilder
from ttkbootstrap.style.tokens import FontTokenType, ForegroundToken
from ttkbootstrap.utils import unsnake_kwargs


class Label(BaseWidget):
    """A themed label widget with support for signals and color tokens."""

    _configure_methods = {"text", "text_signal", "color"}

    def __init__(
            self,
            parent,
            text: str = "",
            color: ForegroundToken = None,
            font: FontTokenType = "body",
            **kwargs: Unpack[LabelOptions]
    ):
        """
        Initialize a themed label.

        Args:
            parent: The parent widget.
            text: The label text.
            color: Optional foreground color token (e.g., "primary", "muted").
            font: The font token to use (default is "body").
            **kwargs: Additional ttk.Label options.
        """
        self._text_signal = Signal(text)
        self._style_builder = LabelStyleBuilder(color, **kwargs)
        self._widget = ttk.Label(
            parent,
            font=font,
            textvariable=self._text_signal.var,
            **unsnake_kwargs(kwargs)
        )
        super().__init__(parent)

    def text(self, value: str = None):
        """Get or set the label text."""
        if value is None:
            return self._text_signal()
        self._text_signal.set(value)
        return self

    def text_signal(self, value: Signal[str] = None):
        """Get or set the label text as a signal"""
        if value is None:
            return self._text_signal
        self._text_signal = value
        self.configure(textvariable=self._text_signal.var)
        return self

    def color(self, value: str = None):
        """Get or set the label text color."""
        if value is None:
            return self._style_builder.color()
        else:
            self._style_builder.color(value)
            self.update_style()
            return self
