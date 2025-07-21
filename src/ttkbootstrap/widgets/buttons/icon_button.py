from tkinter import ttk
from typing import Callable, Optional, Unpack

from ttkbootstrap.core.mixins.icon import IconMixin
from ttkbootstrap.core.widget import BaseWidget
from ttkbootstrap.core.libtypes import ButtonOptions
from ttkbootstrap.style.tokens import ButtonVariant, SemanticColor
from ttkbootstrap.style.builders.icon_button import IconButtonStyleBuilder
from ttkbootstrap.utils import unsnake_kwargs


class IconButton(BaseWidget, IconMixin):
    """
    A styled Icon Button widget with fluent configuration
    """

    _configure_methods = {"on_click", "icon", "color", "variant"}

    def __init__(
            self,
            parent,
            icon: str = None,
            color: SemanticColor = "primary",
            variant: ButtonVariant = "solid",
            on_click: Callable = None,
            **kwargs: Unpack[ButtonOptions]
    ):
        """
        Initialize a new Button.

        Args:
            parent: Parent container.
            icon: Optional icon identifier.
            color: Optional color role.
            variant: Optional style variant.
            on_click: Callback function for click events.
            **kwargs: Additional ttk.Button options.
        """
        self._on_click = on_click
        self._style_name: Optional[str] = None
        self._color = color
        self._variant = variant
        self._icon = icon
        build_options = kwargs.pop('builder', dict())
        self._style_builder = IconButtonStyleBuilder(color, variant, **build_options)

        # remove invalid arguments for icon button
        for key in ['compound', 'text']:
            kwargs.pop(key, None)

        self._widget = ttk.Button(
            parent,
            command=on_click,
            compound="image",
            **unsnake_kwargs(kwargs)
        )
        super().__init__(parent)
        IconMixin.__init__(self)

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

    def icon(self, value: str = None):
        """Get or set the icon (unimplemented)."""
        if value is None:
            return self._icon
        else:
            self._icon = value
            self._update_icon_assets()
            return self

    def color(self, value: SemanticColor = None):
        """Get or set the color role (unimplemented)."""
        if value is None:
            return self._color
        else:
            self._color = value
            self._style_builder.color(value)
            self.update_style()
            self._update_icon_assets()
            return self

    def variant(self, value: ButtonVariant = None):
        """Get or set the style variant (unimplemented)."""
        if value is None:
            return self._variant
        else:
            self._variant = value
            self._style_builder.variant(value)
            self.update_style()
            self._update_icon_assets()
            return self

    def enable(self):
        """Enable the button."""
        self.widget.state(['normal'])
        self._toggle_disable_icon(False)
        return self

    def disable(self):
        """Disable the button."""
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
