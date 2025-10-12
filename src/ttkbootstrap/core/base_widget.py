from __future__ import annotations

import inspect
import tkinter as tk
from tkinter import ttk
from typing import Type

from ttkbootstrap.core.layout_context import current_container
from ttkbootstrap.core.mixins.layout import LayoutMixin
from ttkbootstrap.events import Event
from ttkbootstrap.interop.runtime.binding import BindingMixin
from ttkbootstrap.interop.runtime.configure import ConfigureMixin
from ttkbootstrap.interop.runtime.focus import FocusMixin
from ttkbootstrap.interop.runtime.grab import GrabMixIn
from ttkbootstrap.interop.runtime.schedule import Schedule
from ttkbootstrap.interop.runtime.winfo import WidgetInfoMixin
from ttkbootstrap.types import Widget
from ttkbootstrap.utils import resolve_parent, unsnake_kwargs


class BaseWidget(
    BindingMixin,
    LayoutMixin,
    FocusMixin,
    GrabMixIn,
    WidgetInfoMixin,
    ConfigureMixin,
):
    """Core wrapper that creates a Tk/ttk widget and layers ttkbootstrap mixins.

    Responsibilities:
    - Normalize options and create the underlying Tk/ttk widget.
    - Attach a `Schedule` for safe, UI-thread timers.
    - Bind theme-change updates and apply a surface token.
    - Register with the current layout container with an initial layout intent.
    """

    _widget: ttk.Widget
    schedule: Schedule

    def __init__(
            self,
            tk_widget: Type,
            tk_widget_options: dict | None = None,
            *,
            parent: Widget | None = None,
            tk_layout_options: dict | None = None,
            surface: str | None = None,
    ):
        """
        Create the underlying Tk/ttk widget, attach infrastructure, and register layout intent.

        Parameters
        ----------
        tk_widget:
            The concrete Tk/ttk widget class to instantiate (e.g., `ttk.Entry`, `ttk.Button`, `tk.Toplevel`, `tk.Tk`).
        tk_widget_options:
            Keyword options passed directly to the widget constructor. Keys may be in snake_case and
            are normalized via `unsnake_kwargs`.
        parent:
            The *logical* parent used for styling/registration with layout containers. If omitted,
            the current layout context (`current_container()`) is used.
        tk_layout_options:
            Options consumed by mixins and layout registration (e.g., initial layout intent).
        surface:
            Optional theme surface token for this widget. If omitted, the surface is inherited from
            the logical parent (when available).

        Raises
        ------
        RuntimeError
            If no `parent` or active layout container is available for non-root widgets.
        """
        # --- Normalize options ---
        tk_widget_options = dict(tk_widget_options or {})
        tk_layout_options = dict(tk_layout_options or {})

        custom_id = tk_widget_options.pop("id", None)

        # Determine logical parent (container for styling/registration)
        logical_parent = parent if parent is not None else current_container()

        # Identify widget class flavor
        is_class = inspect.isclass(tk_widget)
        is_root_class = is_class and issubclass(tk_widget, tk.Tk)

        # --- Decide Tk master (actual widget parent) ---
        if is_root_class:
            master_ref = None
        else:
            if logical_parent is None:
                raise RuntimeError("No parent or container; cannot create a widget.")
            master_ref = logical_parent

        # Keep references
        self._parent = logical_parent
        self._master_ref = master_ref

        # --- Create the underlying Tk/ttk widget FIRST ---
        tk_kwargs = unsnake_kwargs(tk_widget_options) or {}
        if is_root_class:
            self._widget = tk_widget(**tk_kwargs)  # tk.Tk takes no master
        else:
            master_arg = resolve_parent(self._master_ref)
            self._widget = tk_widget(master_arg, **tk_kwargs)

        # Attached scheduler
        self.schedule = Schedule(self._widget)

        # --- Now run cooperative mixin initializers (safe to bind now) ---
        super().__init__(**tk_layout_options)

        # allow optional 'id' to come by layout options
        from ttkbootstrap.core.widget_registry import register as _register
        _register(self, custom_id=custom_id)

        # Theme surface & binding
        self._surface_token = surface
        self.on(Event.THEME_CHANGED).listen(lambda _: self.update_style())

        # Auto-register with the *logical* container (if any)
        container = self._parent
        if container and hasattr(container, "register_layout_child"):
            # Infer an initial layout method (same heuristics as before)
            method = None
            if str(container) == ".":
                method = "pack"
            elif hasattr(container, "preferred_layout_method"):
                try:
                    m = container.preferred_layout_method()
                    if m in ("grid", "pack", "place"):
                        method = m
                except Exception:
                    method = None
            if method is None:
                name = type(container).__name__.lower()
                if hasattr(container, "_mount_child_grid") or "grid" in name:
                    method = "grid"
                elif hasattr(container, "_mount_child_pack") or "pack" in name:
                    method = "pack"
                else:
                    method = "grid"

            # Save empty intent and register; container will flush during context exit
            self._saved_layout = (method, {})
            self._pending_parent = container
            container.register_layout_child(self, method, {})

    # ---- Properties / Utilities unchanged below ----
    @property
    def parent(self):
        """Return the logical parent/container used for layout and style inheritance."""
        return self._parent

    @property
    def tk_name(self):
        """The tcl/tk pathname"""
        return str(self._widget)

    @property
    def widget(self) -> ttk.Widget:
        """Return the underlying Tk/ttk widget instance."""
        return self._widget

    @property
    def tk(self):
        """Return the Tcl interpreter handle (`tkapp`) of the underlying widget."""
        return self.widget.tk

    @property
    def surface_token(self):
        """Return the effective theme surface token, inheriting from parent when unset."""
        if self._surface_token is not None:
            return self._surface_token
        return getattr(self._parent, "surface_token", None) if self._parent is not None else None

    @property
    def custom_id(self) -> str | None:
        from ttkbootstrap.core.widget_registry import get_id as _get_id
        return _get_id(self)

    @custom_id.setter
    def custom_id(self, value: str | None) -> None:
        from ttkbootstrap.core.widget_registry import set_id as _set_id
        _set_id(self, value)

    def destroy(self):
        """Destroy the underlying widget."""
        try:
            from ttkbootstrap.core.widget_registry import unregister as _unregister
            _unregister(self)
        finally:
            self.widget.destroy()

    def is_ttk(self) -> bool:
        """True if the underlying widget is a ttk widget (class name starts with 'T')."""
        return self.widget_class().startswith("T")

    def state(self, value: str | list[str] | tuple[str, ...] = None):
        """Pass-through to ttk's `state()` for getting/setting widget state flags."""
        return self.widget.state(value)

    def update_style(self):
        """Rebuild and apply the computed style when a theme/surface change occurs."""
        if hasattr(self, "_style_builder"):
            self._style_builder.surface(self.surface_token)
            style_name = self._style_builder.build()
            if "tkinter" in style_name:
                pass
            else:
                self.configure(style=style_name)

    def __str__(self):
        """Return the Tk path name of the underlying widget."""
        return str(self.__class__.__name__)

    def __repr__(self):
        """Debug representation; returns the Tk path name."""
        return str(self.__class__.__name__)
