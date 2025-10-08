from __future__ import annotations

from tkinter import ttk
from typing import Unpack, cast

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.core.mixins.icon import IconMixin
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.style.types import ForegroundColor, SurfaceColor, TypographyToken
from ttkbootstrap.types import Compound, IconPosition, Variable
from ttkbootstrap.utils import assert_valid_keys, merge_build_options, normalize_icon_position, resolve_options
from ttkbootstrap.widgets.label.style import LabelStyleBuilder
from ttkbootstrap.widgets.label.types import LabelOptions


class Label(BaseWidget, IconMixin):
    """A themed label widget with support for signals and color tokens."""

    widget: ttk.Label
    _configure_methods = {
        "text": "_configure_text",
        "foreground": "_configure_foreground",
        "background": "_configure_background",
        "compound": "_configure_compound",
        "text_variable": "_configure_text_variable",
        "signal": "_configure_text_signal",
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
            **kwargs: Unpack[LabelOptions]
    ):
        """Initialize a themed label.

        Args:
            text: The label text.
            foreground: Optional foreground color override (e.g., "primary", "secondary-subtle").
            background: Optional background color override (e.g., "gray-200", "layer-2").
            font: The font token to use (default is "body").
            variant: The visual variant of the label
            icon: The icon to display
            **kwargs: Additional Label options.

        Keyword Args:
            anchor: Specifies how the information in the widget is positioned relative to the inner margins.
            builder: Key-value options passed to the style builder.
            compound: Specifies the relative position of the image and text.
            cursor: Mouse cursor to display when hovering over the label.
            image: An image to display in the label, such as a PhotoImage, BootstrapIcon, or LucideIcon.
            justify: Specifies how the lines are laid out relative to one another with multiple lines of text.
            padding: Space around the label content.
            take_focus: Specifies if the widget accepts focus during keyboard traversal.
            text_variable: A tkinter variable bound to the label text.
            underline: The integer index (0-based) of a character to underline in the text.
            width: The width of the widget in pixels.
            wrap_length: The maximum line length in pixels.
        """
        self._text_signal = text if isinstance(text, Signal) else Signal(text)
        self._icon = resolve_options(icon, 'name') if icon else None

        # set initial icon position
        self._has_text = len(str(self._text_signal()) or "") > 0
        self._has_icon = icon is not None
        self._compound = kwargs.pop('compound', 'auto')

        compound = normalize_icon_position(self._compound, has_text=self._has_text, has_icon=self._has_icon)
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

    @property
    def signal(self):
        """The signal bound to the label text"""
        return self._text_signal

    def update_style(self):
        """INTERNAL --- Update the widget style and bind stateful icons"""
        super().update_style()
        if self._icon:
            self._bind_stateful_icons()

    # ----- Configuration delegates -----

    def _configure_text(self, value: str = None):
        """Get or set the label text."""
        if value is None:
            return self._text_signal()
        self._text_signal.set(value)
        self._has_text = len(value) > 0
        if self._compound == "auto":
            # force automatic adjustment
            self._configure_compound("auto")
        return self

    def _configure_text_signal(self, value: Signal[str] = None):
        """Get or set the label text as a signal"""
        if value is None:
            return self._text_signal
        if self._text_signal:
            self._text_signal.unsubscribe_all()
        self._text_signal = value
        self.configure(textvariable=self._text_signal.var)
        return self

    def _configure_text_variable(self, value: Variable = None):
        if value is None:
            return self._text_signal
        else:
            return self._configure_text_signal(Signal.from_variable(value))

    def _configure_foreground(self, value: ForegroundColor = None):
        if value is None:
            return self._style_builder.options('foreground')
        else:
            self._style_builder.options(foreground=value)
            self.update_style()
            return self

    def _configure_background(self, value: SurfaceColor = None):
        if value is None:
            return self._style_builder.options('background')
        else:
            self._style_builder.options(background=value)
            self.update_style()
            return self

    def _configure_compound(self, value: IconPosition = None):
        if value is None:
            return self._compound
        else:
            self._compound = value
            compound = normalize_icon_position(value, has_text=self._has_text, has_icon=self._has_icon)
            self.widget.configure(compound=cast(Compound, compound))
            if not self._has_text:
                self._style_builder.options(icon_only=True)
            else:
                self._style_builder.options(icon_only=False)
            return self
