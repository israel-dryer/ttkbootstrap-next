from __future__ import annotations
from tkinter import ttk
from typing import Unpack

from ttkbootstrap.types import Anchor, Compound, IconPosition, Image, Justify, Padding, CoreOptions
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.core.mixins.icon import IconMixin
from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.style.builders.label import LabelStyleBuilder
from ttkbootstrap.utils import assert_valid_keys, merge_build_options, normalize_icon_position, resolve_options
from ttkbootstrap.style.types import ForegroundColor, SurfaceColor, TypographyToken


class LabelOptions(CoreOptions, total=False):
    """Optional keyword arguments accepted by the `Label` widget.

    Attributes:
        anchor: Specifies how the information in the widget is positioned relative to the inner margins.
        compound: Specifies the relative position of the image and text.
        cursor: Mouse cursor to display when hovering over the label.
        image: An image to display in the label, such as a PhotoImage, BootstrapIcon, or LucideIcon.
        justify: Specifies how the lines are laid out relative to one another with multiple lines of text.
        padding: Space around the label content.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        underline: The integer index (0-based) of a character to underline in the text.
        width: The width of the widget in pixels.
        wrap_length: The maximum line length in pixels.
        builder: key-value options passed to the style builder
    """
    anchor: Anchor
    compound: Compound
    cursor: str
    image: Image
    justify: Justify
    padding: Padding
    take_focus: bool
    underline: int
    width: int
    wrap_length: int
    builder: dict


class Label(BaseWidget, IconMixin):
    """A themed label widget with support for signals and color tokens."""

    widget: ttk.Label
    _configure_methods = {
        "text": "text",
        "text_signal": "text_signal",
        "foreground": "foreground",
        "background": "background",
        "icon_position": "icon_position"
    }

    def __init__(
            self,
            text: str | Signal = "",
            *,
            foreground: ForegroundColor = None,
            background: SurfaceColor = None,
            font: TypographyToken = "body",
            variant: str = "default",
            icon: str | dict = None,
            icon_position: IconPosition = "auto",
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
            icon: The icon to display
            icon_position: The position of the icon in the label.
            **kwargs: Additional Label options.
        """
        self._text_signal = text if isinstance(text, Signal) else Signal(text)
        self._icon = resolve_options(icon, 'name') if icon else None

        # set initial icon position
        self._has_text = len(str(self._text_signal()) or "") > 0
        self._has_icon = icon is not None
        self._icon_position = icon_position

        compound = normalize_icon_position(icon_position, has_text=self._has_text, has_icon=self._has_icon)
        kwargs.pop('compound', None)
        parent = kwargs.pop('parent', None)
        assert_valid_keys(kwargs, LabelOptions, where="Label")

        # style builder options
        build_options = merge_build_options(
            kwargs.pop('builder', {}),
            foreground=foreground,
            background=background,
            variant=variant
        )
        self._style_builder = LabelStyleBuilder(**build_options)

        tk_options = dict(
            font=font,
            textvariable=self._text_signal.var,
            compound=compound,
            **kwargs
        )
        super().__init__(ttk.Label, tk_options, parent=parent)
        IconMixin.__init__(self)

    def text(self, value: str = None):
        """Get or set the label text."""
        if value is None:
            return self._text_signal()
        self._text_signal.set(value)
        self._has_text = len(value) > 0
        if self._icon_position == "auto":
            # force automatic adjustment
            self.icon_position("auto")
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
            return self._style_builder.options('foreground')
        else:
            self._style_builder.options(foreground=value)
            self.update_style()
            return self

    def background(self, value: SurfaceColor = None):
        """Get or set the label background color."""
        if value is None:
            return self._style_builder.options('background')
        else:
            self._style_builder.options(background=value)
            self.update_style()
            return self

    def icon_position(self, value: IconPosition = None):
        """Get or set the position of the icon in the label"""
        if value is None:
            return self._icon_position
        else:
            self._icon_position = value
            compound: Compound = normalize_icon_position(value, has_text=self._has_text, has_icon=self._has_icon)
            self.widget.configure(compound=compound)
            return self

    def update_style(self):
        """Update the widget style and bind stateful icons"""
        super().update_style()
        if self._icon:
            self._bind_stateful_icons()
