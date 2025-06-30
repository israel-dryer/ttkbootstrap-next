from tkinter import ttk
from typing import Callable, Optional

from ttkbootstrap.core import Signal
from ttkbootstrap.core.widget import BaseWidget


class Button(BaseWidget):
    """
    A styled Button widget with fluent configuration and reactive text binding.
    """

    _configure_methods = {"text", "text_signal", "on_click", "icon", "color", "variant"}

    def __init__(
            self,
            parent,
            text: str,
            icon: str = None,
            color: str = None,
            variant: str = None,
            on_click: Callable = None,
            **kwargs
    ):
        """
        Initialize a new Button.

        Args:
            parent: Parent container.
            text: Initial label text.
            icon: Optional icon identifier (not implemented).
            color: Optional color role.
            variant: Optional style variant.
            on_click: Callback function for click events.
            **kwargs: Additional ttk.Button options.
        """
        self._on_click = on_click
        self._text_signal = Signal(text)
        self._style_name: Optional[str] = None

        self._color = color
        self._variant = variant
        self._icon = icon

        self._widget = ttk.Button(
            parent,
            command=on_click,
            textvariable=self._text_signal.name,
            **kwargs
        )

        super().__init__(parent)

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
        self.configure(textvariable=self._text_signal.name)
        return self

    def icon(self, value: str = None):
        """Get or set the icon (unimplemented)."""
        pass

    def color(self, value: str = None):
        """Get or set the color role (unimplemented)."""
        pass

    def variant(self, value: str = None):
        """Get or set the style variant (unimplemented)."""
        pass

    def enable(self):
        """Enable the button."""
        self.configure(state="normal")
        return self

    def disable(self):
        """Disable the button."""
        self.configure(state="disabled")
        return self

    def invoke(self):
        """Trigger a button click programmatically."""
        self.widget.invoke()
