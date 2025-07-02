from tkinter import ttk
from typing import Callable, Optional

from ttkbootstrap.core.widget import BaseWidget
from ..style.builders.icon_button import IconButtonStyleBuilder


class IconButton(BaseWidget):
    """
    A styled Icon Button widget with fluent configuration
    """

    _configure_methods = {"on_click", "icon", "color", "variant"}

    def __init__(
            self,
            parent,
            icon: str = None,
            color: str = "primary",
            size: str = "md",
            variant: str = "solid",
            on_click: Callable = None,
            **kwargs
    ):
        """
        Initialize a new Button.

        Args:
            parent: Parent container.
            icon: Optional icon identifier.
            color: Optional color role.
            size: Optional size.
            variant: Optional style variant.
            on_click: Callback function for click events.
            **kwargs: Additional ttk.Button options.
        """
        self._on_click = on_click
        self._style_name: Optional[str] = None
        self._color = color
        self._variant = variant
        self._size = size
        self._icon = icon
        self._stateful_icons_bound = False
        self._style_builder = IconButtonStyleBuilder(color, variant, size)

        # remove invalid arguments for icon button
        for key in ['compound', 'text']:
            kwargs.pop(key, None)

        self._widget = ttk.Button(
            parent,
            command=on_click,
            compound="image",
            **kwargs
        )
        super().__init__(parent)
        self._update_icon_assets()

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

    def color(self, value: str = None):
        """Get or set the color role (unimplemented)."""
        if value is None:
            return self._color
        else:
            self._color = value
            self._style_builder.color(value)
            self.update_style()
            self._update_icon_assets()
            return self

    def variant(self, value: str = None):
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

    def _update_icon_assets(self):
        self._style_builder.build_solid_icon_assets(self._icon)
        if not self._stateful_icons_bound:
            self._bind_stateful_icons()
        disabled = 'disabled' in self.widget.state()
        self._toggle_disable_icon(disabled)

    def _bind_stateful_icons(self):
        if self._stateful_icons_bound:
            return
        icons = self._style_builder.stateful_icons
        self.configure(image=icons['normal'])

        on_enter = lambda _: None if "disabled" in self.widget.state() else self.configure(image=icons['hover'])
        on_leave = lambda _: None if "disabled" in self.widget.state() else self.configure(image=icons['normal'])
        on_press = lambda _: None if "disabled" in self.widget.state() else self.configure(image=icons['pressed'])
        on_focus_in = lambda _: None if "disabled" in self.widget.state() else self.configure(image=icons['focus'])
        on_focus_out = lambda _: None if "disabled" in self.widget.state() else self.configure(image=icons['normal'])

        self.bind('<Enter>', on_enter)
        self.bind('<Leave>', on_leave)
        self.bind('<FocusIn>', on_focus_in)
        self.bind('<FocusOut>', on_focus_out)
        self.bind('<ButtonPress-1>', on_press)
        self._stateful_icons_bound = True

        # set disabled state
        if 'disabled' in self.widget.state():
            self.configure(image=icons['disabled'], compound="left")

    def _toggle_disable_icon(self, disable=True):
        icons = self._style_builder.stateful_icons
        if disable:
            self.configure(image=icons['disabled'])
        else:
            self.configure(image=icons['normal'])
