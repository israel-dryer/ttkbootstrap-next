from tkinter import ttk
from typing import Callable, Literal, Unpack

from ttkbootstrap.core import Signal
from ttkbootstrap.core.mixins.icon import IconMixin
from ttkbootstrap.core.widget import BaseWidget
from ttkbootstrap.core.libtypes import ButtonOptions
from ttkbootstrap.style.tokens import ButtonVariant, SemanticColor
from ttkbootstrap.style.builders.button import ButtonStyleBuilder
from ttkbootstrap.utils import unsnake_kwargs


class Button(BaseWidget, IconMixin):
    """
    A styled Button widget with fluent configuration and reactive text binding.
    """

    _configure_methods = {"text", "text_signal", "on_click", "icon", "icon_position", "color", "variant"}

    def __init__(
            self,
            parent,
            text: str,
            color: SemanticColor = None,
            variant: ButtonVariant = "solid",
            icon: str = None,
            icon_position: Literal['left', 'right'] = 'left',
            on_click: Callable = None,
            **kwargs: Unpack[ButtonOptions]
    ):
        """
        Initialize a new Button.

        Args:
            parent: Parent container.
            text: Initial label text.
            color: Optional color role.
            variant: Optional style variant.
            icon: Optional icon identifier.
            icon_position: The position of the icon in the button.
            on_click: Callback function for click events.
            **kwargs: Additional ttk.Button options.
        """
        self._on_click = on_click
        self._text_signal = Signal(text)
        self._icon = icon
        self._icon_position = icon_position
        self._style_builder = ButtonStyleBuilder(color, variant)

        # remove invalid arguments
        for key in ['compound']:
            kwargs.pop(key, None)

        self._widget = ttk.Button(
            parent,
            command=on_click,
            compound=self._icon_position if self._icon else "text",
            textvariable=self._text_signal.var,
            **unsnake_kwargs(kwargs)
        )
        super().__init__(parent)
        IconMixin.__init__(self)
        self.update_style()

    def is_disabled(self):
        """Indicates if button is in a disabled state"""
        return "disabled" in self.widget.state()

    def on_click(self, func: Callable = None):
        """Get or set the button click handler."""
        if func is None:
            return self._on_click
        if not callable(func):
            raise TypeError(f"`on_click` must be callable, got {type(func).__name__}")
        self._on_click = func
        self.configure(command=func)
        return self

    def text(self, value: str = None):
        """Get or set the button text."""
        if value is None:
            return self._text_signal()
        self._text_signal.set(value)
        return self

    def text_signal(self, value: Signal[str] = None):
        """Get or set the button text signal."""
        if value is None:
            return self._text_signal
        self._text_signal = value
        self.configure(textvariable=self._text_signal.var)
        return self

    def icon_position(self, value: Literal['left', 'right'] = None):
        """Get or set the position of the icon in the button"""
        if value is None:
            return self._icon_position
        else:
            self._icon_position = value
            self.widget.configure(compound=value)
            return self

    def color(self, value: SemanticColor = None):
        """Get or set the color role"""
        if value is None:
            return self._style_builder.color()
        else:
            self._style_builder.color(value)
            self.update_style()
            self._update_icon_assets()
            return self

    def variant(self, value: ButtonVariant = None):
        """Get or set the style variant."""
        if value is None:
            return self._style_builder.variant()
        else:
            self._style_builder.variant(value)
            self.update_style()
            self._update_icon_assets()
            return self

    def enable(self):
        """Enable the button."""
        self.widget.state(['normal'])
        if self.icon():
            self._toggle_disable_icon(False)
        return self

    def disable(self):
        """Disable the button."""
        if self.icon():
            self._toggle_disable_icon(True)
        self.state(['disabled'])
        return self

    def invoke(self):
        """Trigger a button click programmatically."""
        self.widget.invoke()

    def update_style(self):
        """Update the widget style and bind stateful icons"""
        super().update_style()
        if self._icon:
            self._bind_stateful_icons()
