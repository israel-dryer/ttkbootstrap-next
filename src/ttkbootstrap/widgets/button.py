from tkinter import ttk
from typing import Callable, Literal, Optional, Union, Unpack, cast

from ttkbootstrap.types import Compound, IconPosition, Padding, CoreOptions
from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.core.mixins.icon import IconMixin
from ttkbootstrap.utils import assert_valid_keys, normalize_icon_position, resolve_options
from ttkbootstrap.style.builders.button import ButtonStyleBuilder
from ttkbootstrap.style.types import ButtonVariant, SemanticColor


class ButtonOptions(CoreOptions, total=False):
    """
    Defines the optional keyword arguments accepted by the `Button` widget.

    Attributes:
        default: Used to set the button that is designated as "default"; in a dialog for example.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        underline: The integer index (0-based) of a character to underline in the text.
        width: The width of the widget in pixels.
        builder: key-value options passed to the style builder
        padding: The padding of the widget in pixels.
        position: Whether to use static, absolute or fixed positioning.
    """
    default: Literal['normal', 'active', 'disabled']
    cursor: str
    take_focus: bool
    underline: int
    width: int
    builder: dict
    padding: Padding


class Button(BaseWidget, IconMixin):
    """
    A styled Button widget with fluent configuration and reactive text binding.
    """

    widget: ttk.Button
    _configure_methods = {
        "text": "text",
        "text_signal": "text_signal",
        "on_click": "on_click",
        "icon": "icon",
        "icon_position": "icon_position",
        "color": "color",
        "variant": "variant"
    }

    def __init__(
            self,
            text: str | Signal = "",
            color: Union[SemanticColor, str] = None,
            variant: ButtonVariant = "solid",
            icon: str | dict = None,
            icon_position: IconPosition = "auto",
            on_click: Callable = None,
            **kwargs: Unpack[ButtonOptions]
    ):
        """
        Initialize a new Button.

        Args:
            text: Initial label text.
            color: Optional color role.
            variant: Optional style variant.
            icon: Optional icon identifier.
            icon_position: The position of the icon in the button.
            on_click: Callback function for click events.
            **kwargs: Additional Button options.
        """
        self._on_click = on_click
        self._text_signal = text if isinstance(text, Signal) else Signal(text)
        self._icon = resolve_options(icon, 'name') or None
        self._has_text = len(text) > 0
        self._has_icon = icon is not None
        build_options = kwargs.pop('builder', dict())
        build_options['icon_only'] = not self._has_text
        self._icon_position = icon_position
        self._style_builder = ButtonStyleBuilder(color, variant, **build_options)

        kwargs.pop('compound', None)
        compound = normalize_icon_position(icon_position, has_text=self._has_text, has_icon=self._has_icon)
        parent = kwargs.pop('parent', None)
        assert_valid_keys(kwargs, ButtonOptions, where="Button")

        tk_options = dict(
            command=on_click,
            compound=compound,
            textvariable=self._text_signal.var,
            **kwargs
        )
        super().__init__(ttk.Button, tk_options, parent=parent)
        IconMixin.__init__(self)

    def is_disabled(self):
        """Indicates if button is in a disabled state"""
        return "disabled" in self.widget.state()

    def on_click(self, func: Optional[Callable] = None):
        """Get or set the button click handler."""
        if func is None:
            return self._on_click
        if func is not None and callable(func):
            self._on_click = func
            self.configure(command=func)
        else:
            raise TypeError(f"`on_click` must be callable, got {type(func).__name__}") from None
        return self

    def text(self, value: str = None):
        """Get or set the button text."""
        if value is None:
            return self._text_signal()
        self._text_signal.set(value)
        self._has_text = len(value) > 0
        if self._icon_position == "auto":
            self.icon_position("auto")  # force automatic adjustment
        return self

    def text_signal(self, value: Signal[str] = None):
        """Get or set the button text signal."""
        if value is None:
            return self._text_signal
        self._text_signal = value
        self.widget.configure(textvariable=self._text_signal.var)
        return self

    def icon_position(self, value: IconPosition = None):
        """Get or set the position of the icon in the button"""
        if value is None:
            return self._icon_position
        else:
            self._icon_position = value
            compound = normalize_icon_position(value, has_text=self._has_text, has_icon=self._has_icon)
            self.widget.configure(compound=cast(Compound, compound))
            if not self._has_text:
                self._style_builder.icon_only(True)
            else:
                self._style_builder.icon_only(False)
            return self

    def color(self, value: str = None):
        """Get or set the color role"""
        if value is None:
            return self._style_builder.color()
        else:
            self._style_builder.color(value)
            # self._update_icon_assets()
            self.update_style()
            return self

    def variant(self, value: str = None):
        """Get or set the style variant."""
        if value is None:
            return self._style_builder.variant()
        else:
            self._style_builder.variant(value)
            # self._update_icon_assets()
            self.update_style()
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
