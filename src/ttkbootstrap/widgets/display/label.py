from tkinter import ttk
from typing import Unpack

from ttkbootstrap.core import Signal
from ttkbootstrap.core.libtypes import LabelOptions
from ttkbootstrap.core.widget import BaseWidget
from ttkbootstrap.style.builders.label import LabelStyleBuilder
from ttkbootstrap.style.tokens import TypographyToken, ForegroundColor, SurfaceColor
from ttkbootstrap.utils import unsnake_kwargs


class Label(BaseWidget):
    """A themed label widget with support for signals and color tokens."""

    _configure_methods = {"text", "text_signal", "foreground", "background"}

    def __init__(
            self,
            parent,
            text: str = "",
            foreground: ForegroundColor = None,
            background: SurfaceColor= None,
            font: TypographyToken = "body",
            variant: str = "default",
            **kwargs: Unpack[LabelOptions]
    ):
        """
        Initialize a themed label.

        Args:
            parent: The parent widget.
            text: The label text.
            foreground: Optional foreground color override (e.g., "primary", "secondary-subtle").
            background: Optional background color override (e.g., "gray-200", "layer-2").
            font: The font token to use (default is "body").
            variant: The visual variant of the label
            **kwargs: Additional ttk.Label options.
        """
        self._text_signal = Signal(text)
        self._style_builder = LabelStyleBuilder(foreground, background, variant)
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

    def foreground(self, value: ForegroundColor = None):
        """Get or set the label text color."""
        if value is None:
            return self._style_builder.foreground()
        else:
            self._style_builder.foreground(value)
            self.update_style()
            return self

    def background(self, value: SurfaceColor = None):
        """Get or set the label background color."""
        if value is None:
            return self._style_builder.background()
        else:
            self._style_builder.background(value)
            self.update_style()
            return self