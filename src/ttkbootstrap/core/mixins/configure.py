from typing import Any

from ttkbootstrap.types import Widget
from ttkbootstrap.utils import unsnake, unsnake_kwargs


class ConfigureMixin:
    """Mixin that provides unified configuration access for widgets."""

    widget: Widget
    _configure_methods: dict

    def configure(self, option: str = None, **kwargs) -> Any:
        """Get or set widget configuration.

        Args:
            option: A single option name to retrieve. If None, will apply settings via keyword arguments.
            **kwargs: Keyword arguments to configure the widget.

        Returns:
            The current value of a configuration option if `option` is provided,
            otherwise the result of applying the configuration.
        """
        if option is not None:
            return self._get_config(option)
        else:
            self._set_config(**kwargs)
            return self

    def _set_config(self, **kwargs) -> None:
        """Apply configuration options to the widget.

        Custom configuration methods in `_configure_methods` are dispatched
        and removed from `kwargs` before calling `widget.configure()`.
        """
        if hasattr(self, "_configure_methods"):
            for key in list(kwargs):
                if key in list(self._configure_methods.keys()):
                    method = getattr(self, self._configure_methods[key])
                    if callable(method):
                        method(kwargs.pop(key))  # dispatch and remove
        self.widget.configure(**unsnake_kwargs(kwargs))

    def _get_config(self, option: str) -> Any:
        """Retrieve the value of a single configuration option.

        Args:
            option: The name of the option to retrieve.

        Returns:
            The current value of the requested option.
        """
        if hasattr(self, "_configure_methods") and option in self._configure_methods.keys():
            method = getattr(self, self._configure_methods[option])
            if callable(method):
                return method()
        return self.widget.cget(unsnake(option))
