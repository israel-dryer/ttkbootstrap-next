from tkinter import Variable, ttk
from typing import Callable, Optional, Union, Unpack, cast

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.core.mixins.icon import IconMixin
from ttkbootstrap.events import Event
from ttkbootstrap.interop.runtime.binding import Stream, Subscription
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.style.types import SemanticColor
from ttkbootstrap.types import AltEventHandler, Compound, IconPosition
from ttkbootstrap.utils import assert_valid_keys, merge_build_options, normalize_icon_position, resolve_options
from ttkbootstrap.widgets.button.events import ButtonInvokeEvent
from ttkbootstrap.widgets.button.style import ButtonStyleBuilder
from ttkbootstrap.widgets.button.types import ButtonOptions, ButtonVariant


class Button(BaseWidget, IconMixin):
    """
    A styled Button widget with fluent configuration and reactive text binding.
    """

    widget: ttk.Button
    _configure_methods = {
        "text": "_configure_text",
        "icon": "_configure_icon",
        "compound": "_configure_compound",
        "color": "_configure_color",
        "variant": "_configure_variant",
        "signal": "_configure_text_signal",
        "text_variable": "_configure_text_variable",
        "command": "_configure_command",
    }

    def __init__(
            self,
            text: str | Signal = "",
            *,
            color: Union[SemanticColor, str] = "primary",
            variant: ButtonVariant = "solid",
            icon: str | dict = None,
            command: Optional[Callable] = None,
            **kwargs: Unpack[ButtonOptions]
    ):
        """
        Initialize a new Button.

        Args:
            text: Initial label text.
            color: Optional color role.
            variant: Optional style variant.
            icon: Optional icon identifier.
            command: Callback fired when the button is invoked.
            **kwargs: Additional Button options.
        """
        self._text_signal = text if isinstance(text, Signal) else Signal(text)
        self._icon = resolve_options(icon, 'name') or None
        self._has_text = bool((self._text_signal() or ""))
        self._has_icon = icon is not None
        self._compound = kwargs.pop('compound', 'auto')
        self._command = command
        self._command_sub: Optional[Subscription] = None

        # style builder options
        build_options = merge_build_options(
            kwargs.pop('builder', {}),
            icon_only=not self._has_text,
            color=color,
            variant=variant
        )
        self._style_builder = ButtonStyleBuilder(**build_options)

        compound = normalize_icon_position(self._compound, has_text=self._has_text, has_icon=self._has_icon)
        parent = kwargs.pop('parent', None)
        assert_valid_keys(kwargs, ButtonOptions, where="Button")

        tk_options = dict(
            compound=compound,
            command=self._handle_invoke,
            textvariable=self._text_signal.var,
            **kwargs
        )
        super().__init__(ttk.Button, tk_options, parent=parent)
        if command:
            self._configure_command(command)

    @property
    def signal(self):
        """The signal bound to the button text"""
        return self._text_signal

    def is_disabled(self):
        """Indicates if button is in a disabled state"""
        return "disabled" in self.widget.state()

    def enable(self):
        """Enable the button."""
        self.widget.state(['normal'])
        if self.configure('icon'):
            self._toggle_disable_icon(False)
        return self

    def disable(self):
        """Disable the button."""
        if self.configure('icon'):
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

    # ---- Event handlers -----

    def _handle_invoke(self, *_):
        """Trigger the <<Invoke>> event"""
        self.emit(Event.INVOKE, when="tail")

    def on_invoke(self) -> Stream[ButtonInvokeEvent]:
        """Convenience alias for the invoke stream"""
        return self.on(Event.INVOKE)

    # ---- Configuration delegates -----

    def _configure_command(self, value: AltEventHandler = None):
        if value is None:
            return self._command
        else:
            if self._command_sub is not None:
                self._command_sub.unlisten()
            self._command_sub = self.on_invoke().tap(lambda _: value()).then_stop()
            return self

    def _configure_text(self, value: str = None):
        if value is None:
            return self._text_signal()
        self._text_signal.set(value)
        self._has_text = len(value) > 0
        if self._compound == "auto":
            self._configure_compound("auto")  # force automatic adjustment
        return self

    def _configure_text_signal(self, value: Signal[str] = None):
        if value is None:
            return self._text_signal
        if self._text_signal:
            self._text_signal.unsubscribe_all()
        self._text_signal = value
        self.widget.configure(textvariable=self._text_signal.var)
        return self

    def _configure_text_variable(self, value: Variable = None):
        if value is None:
            return self._text_signal
        else:
            return self._configure_text_signal(Signal.from_variable(value))

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

    def _configure_color(self, value: str = None):
        if value is None:
            return self._style_builder.options("color")
        else:
            self._style_builder.options(color=value)
            self.update_style()
            return self

    def _configure_variant(self, value: str = None):
        """Get or set the style variant."""
        if value is None:
            return self._style_builder.options("variant")
        else:
            self._style_builder.options(variant=value)
            self.update_style()
            return self
