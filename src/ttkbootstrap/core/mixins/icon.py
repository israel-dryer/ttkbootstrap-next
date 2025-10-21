from __future__ import annotations

from typing import Any, Callable

from ttkbootstrap.interop.runtime.configure import configure_delegate
from ttkbootstrap.interop.runtime.schedule import Schedule
from ttkbootstrap.utils import resolve_options


class IconMixin:
    _style_builder: Any
    _icon: dict | None
    _has_icon: bool
    exists: Callable[[], bool]
    is_disabled: Callable[[], bool]
    configure: Callable
    process_idle_tasks: Callable
    has_focus: Callable[[], bool]
    on: Callable
    schedule: Schedule

    def __init__(self, *args, **kwargs):
        # Preserve any icon set by subclasses (e.g., Button.__init__)
        self._icon = getattr(self, "_icon", None)
        self._has_icon = getattr(self, "_has_icon", False)
        super().__init__(*args, **kwargs)

    @configure_delegate("icon")
    def _configure_icon(self, value=None):
        """Get or set the widget icon"""
        if value is None:
            return self._icon

        key_value = resolve_options(value, "name")
        self._style_builder.options(icon=key_value)
        self._has_icon = True
        self.configure(compound="auto")
        self._style_builder.build()

        return self
