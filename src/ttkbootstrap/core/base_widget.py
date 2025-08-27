from __future__ import annotations

import inspect
import tkinter as tk
from tkinter import ttk
from typing import Callable, Literal, Type

from ttkbootstrap.common.types import Widget
from ttkbootstrap.common.utils import unsnake_kwargs, resolve_parent
from ttkbootstrap.core.layout_context import current_container
from ttkbootstrap.core.mixins.binding import BindingMixin
from ttkbootstrap.core.mixins.configure import ConfigureMixin
from ttkbootstrap.core.mixins.focus import FocusMixIn
from ttkbootstrap.core.mixins.grab import GrabMixIn
from ttkbootstrap.core.mixins.layout import LayoutMixin
from ttkbootstrap.core.mixins.winfo import WidgetInfoMixin

PositionType = Literal["static", "absolute", "fixed"]


class BaseWidget(
    BindingMixin,  # init
    FocusMixIn,
    GrabMixIn,
    WidgetInfoMixin,
    ConfigureMixin,
    LayoutMixin  # init
):
    _widget: ttk.Widget

    def __init__(
            self,
            tk_widget: Type,
            tk_widget_options: dict | None = None,
            *,
            parent: Widget | None = None,
            tk_layout_options: dict | None = None,
            surface: str | None = None,
    ):
        # --- Normalize options ---
        tk_widget_options = dict(tk_widget_options or {})
        tk_layout_options = dict(tk_layout_options or {})

        # Position is accepted in either layout or widget opts
        position = tk_widget_options.pop("position", "static")
        tk_layout_options.setdefault("position", position)

        # Initialize LayoutMixin first (establishes _position, etc.)
        LayoutMixin.__init__(self, **tk_layout_options)

        # Determine logical parent (container for styling/registration)
        logical_parent = parent if parent is not None else current_container()

        # Figure out if we're building a true root (tk.Tk subclass)
        is_class = inspect.isclass(tk_widget)
        is_root_class = is_class and issubclass(tk_widget, tk.Tk)
        is_toplevel_class = is_class and issubclass(tk_widget, tk.Toplevel)

        # --- Decide Tk master (actual widget parent) ---
        if is_root_class:
            # True root: master is None; allowed to have no container/parent
            master_ref = None
        else:
            if logical_parent is None:
                # No container provided and not a root: that's an error
                raise RuntimeError("No parent or container; cannot create a widget.")
            # For fixed, parent to the window’s toplevel; else parent to the logical container
            master_ref = logical_parent.widget.winfo_toplevel() if self._position == "fixed" else logical_parent

        # Keep references
        self._parent = logical_parent  # may be None for roots
        self._master_ref = master_ref  # None for roots (tk.Tk)

        # Initialize the rest of the mixins
        super().__init__()

        # --- Create the underlying Tk/ttk widget ---
        tk_kwargs = unsnake_kwargs(tk_widget_options) or {}

        if is_root_class:
            # tk.Tk() takes no master
            self._widget = tk_widget(**tk_kwargs)
        else:
            # Toplevel/ttk widgets take a master
            master_arg = resolve_parent(self._master_ref)
            # If it's a Toplevel with master None and no default root exists yet,
            # Tk will create a default root implicitly; but we typically have a root already.
            if is_toplevel_class and master_arg is None:
                # Create it anyway; Tk will bind to default root.
                self._widget = tk_widget(master_arg, **tk_kwargs)
            else:
                self._widget = tk_widget(master_arg, **tk_kwargs)

        # Theme surface & binding
        self._surface_token = surface
        self.bind("theme-changed", lambda _: self.update_style())

        # Auto-register with the *logical* container (if any)
        container = self._parent
        if container and hasattr(container, "register_layout_child"):
            # Infer an initial layout method (mirror LayoutMixin._infer_layout_method)
            method = None
            if getattr(self, "_position", "static") in ("absolute", "fixed"):
                method = "place"
            elif str(container) == ".":
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

    # ---- Properties ----

    @property
    def parent(self):
        """Logical container parent (may be None for root)."""
        return self._parent

    @property
    def widget(self) -> ttk.Widget:
        return self._widget

    @property
    def tk(self):
        return self.widget.tk

    @property
    def surface_token(self):
        # Inherit from logical container if ours isn't set
        if self._surface_token is not None:
            return self._surface_token
        return getattr(self._parent, "surface_token", None) if self._parent is not None else None

    # ---- Utilities ----

    def schedule(self, ms: int, func: Callable, *args):
        return self.widget.after(ms, func, *args)

    def schedule_after_idle(self, func: Callable, *args):
        return self.widget.after_idle(func, *args)

    def schedule_cancel(self, func_id: str):
        return self.widget.after_cancel(func_id)

    def is_ttk(self) -> bool:
        """Check if the underlying widget is a ttk widget."""
        return self.widget_class().startswith("T")

    def state(self, value: str | list[str] | tuple[str, ...] = None):
        """Get or set the widget state."""
        return self.widget.state(value)

    def destroy(self):
        """Destroy and unregister the widget."""
        self.widget.destroy()

    def update_style(self):
        """Apply theme styling."""
        if hasattr(self, "_style_builder"):
            self._style_builder.surface(self.surface_token)
            style_name = self._style_builder.build()
            if "tkinter" in style_name:
                pass
            else:
                self.configure(style=style_name)

    def __str__(self):
        return str(self._widget)

    def __repr__(self):
        return str(self._widget)
