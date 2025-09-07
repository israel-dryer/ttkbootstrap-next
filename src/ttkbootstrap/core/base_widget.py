from __future__ import annotations

import inspect
import tkinter as tk
from tkinter import ttk
from typing import Callable, Literal, Type

from ttkbootstrap.types import Widget
from ttkbootstrap.events import Event
from ttkbootstrap.utils import unsnake_kwargs, resolve_parent
from ttkbootstrap.core.layout_context import current_container
from ttkbootstrap.interop.runtime.binding import BindingMixin
from ttkbootstrap.interop.runtime.configure import ConfigureMixin
from ttkbootstrap.interop.runtime.focus import FocusMixin
from ttkbootstrap.interop.runtime.grab import GrabMixIn
from ttkbootstrap.core.mixins.layout import LayoutMixin
from ttkbootstrap.interop.runtime.winfo import WidgetInfoMixin

PositionType = Literal["static", "absolute", "fixed"]


class BaseWidget(
    BindingMixin,
    LayoutMixin,
    FocusMixin,
    GrabMixIn,
    WidgetInfoMixin,
    ConfigureMixin,
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

        # Position may be supplied in either dict; keep local for pre-mixin logic
        position = tk_widget_options.pop("position", tk_layout_options.pop("position", "static"))
        tk_layout_options.setdefault("position", position)

        # Determine logical parent (container for styling/registration)
        logical_parent = parent if parent is not None else current_container()

        # Identify widget class flavor
        is_class = inspect.isclass(tk_widget)
        is_root_class = is_class and issubclass(tk_widget, tk.Tk)
        is_toplevel_class = is_class and issubclass(tk_widget, tk.Toplevel)

        # --- Decide Tk master (actual widget parent) ---
        if is_root_class:
            master_ref = None
        else:
            if logical_parent is None:
                raise RuntimeError("No parent or container; cannot create a widget.")
            master_ref = logical_parent.widget.winfo_toplevel() if position == "fixed" else logical_parent

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

        # --- Now run cooperative mixin initializers (safe to bind now) ---
        super().__init__(**tk_layout_options)

        # Theme surface & binding
        self._surface_token = surface
        self.on(Event.THEME_CHANGED).listen(lambda _: self.update_style())

        # Auto-register with the *logical* container (if any)
        container = self._parent
        if container and hasattr(container, "register_layout_child"):
            # Infer an initial layout method (same heuristics as before)
            method = None
            if position in ("absolute", "fixed"):
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

    # ---- Properties / Utilities unchanged below ----
    @property
    def parent(self):
        return self._parent

    @property
    def widget(self) -> ttk.Widget:
        return self._widget

    @property
    def tk(self):
        return self.widget.tk

    @property
    def surface_token(self):
        if self._surface_token is not None:
            return self._surface_token
        return getattr(self._parent, "surface_token", None) if self._parent is not None else None

    def schedule(self, ms: int, func: Callable, *args):
        return self.widget.after(ms, func, *args)

    def schedule_after_idle(self, func: Callable, *args):
        return self.widget.after_idle(func, *args)

    def schedule_cancel(self, func_id: str):
        return self.widget.after_cancel(func_id)

    def is_ttk(self) -> bool:
        return self.widget_class().startswith("T")

    def state(self, value: str | list[str] | tuple[str, ...] = None):
        return self.widget.state(value)

    def destroy(self):
        self.widget.destroy()

    def update_style(self):
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
