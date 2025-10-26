from __future__ import annotations

import tkinter as tk
from typing import Any, Literal, Self, Tuple

from ttkbootstrap_next.core.layout_context import current_container, has_current_container
from ttkbootstrap_next.layouts.types import GridItemOptions, PackItemOptions, PlaceItemOptions
from ttkbootstrap_next.types import Widget
from ttkbootstrap_next.utils import assert_valid_keys, parse_dim

LayoutMethod = Literal["grid", "pack", "place", "widget"]


class LayoutMixin:
    """
    Immediate layout with parental guidance:
      - attach(...): child asks parent for guidance, merges, executes now.
      - hide(): unmanage but KEEP saved layout (grid uses grid_remove()).
      - detach(): unmanage and FORGET saved layout.
    """

    parent: Widget
    widget: tk.Widget

    __layout_saved: Tuple[LayoutMethod, dict[str, Any]] | None

    def __init__(self, *args, **kwargs):
        margin = kwargs.pop("margin", 0)  # ignored for attach(); kept for API stability
        super().__init__(*args, **kwargs)
        self._margin = margin
        self.__layout_saved = None

    # --------------------------- ATTACH -------------------------------
    def attach(self, method: LayoutMethod | None = None, /, **options: Any) -> Self:
        """
        Mount the widget immediately.
        - Determine method (explicit > saved > inferred).
        - Ask parent for guidance (method, options).
        - Merge (guidance first, then child opts win).
        - Execute the chosen geometry manager.
        """
        container = self._resolve_container()

        # Determine method
        if method is not None:
            m_eff: LayoutMethod = method
        elif self.__layout_saved:
            m_eff = self.__layout_saved[0]
        else:
            m_eff = self._infer_layout_method(container)

        # Child-provided (or saved) options
        if options:
            child_opts = dict(options)
        elif self.__layout_saved and self.__layout_saved[0] == m_eff:
            child_opts = dict(self.__layout_saved[1])
        else:
            child_opts = {}

        # Ask parent for guidance
        if hasattr(container, "guide_layout"):
            m_eff, guided = container.guide_layout(self, m_eff, child_opts)
        else:
            guided = {}

        # Merge: parent guidance first, child overrides win
        eff_opts = {**dict(guided), **child_opts}

        # Persist for future empty attach()
        self.__layout_saved = (m_eff, dict(eff_opts))
        setattr(self, "_saved_layout", (m_eff, dict(eff_opts)))

        # Execute with native Tk options only
        if m_eff == "pack":
            # Ensure PackItemOptions includes: side, fill, expand, anchor, padx, pady, ipadx, ipady, etc.
            assert_valid_keys(eff_opts, PackItemOptions, where="pack")
            self.widget.pack(**eff_opts)
            return self

        if m_eff == "grid":
            # Ensure GridItemOptions includes: row, column, rowspan, columnspan, sticky, padx, pady, ipadx, ipady, etc.
            assert_valid_keys(eff_opts, GridItemOptions, where="grid")
            self.widget.grid(**eff_opts)
            return self

        if m_eff == "place":
            # Validate against the *new* PlaceItemOptions (no rel* in public API)
            assert_valid_keys(eff_opts, PlaceItemOptions, where="place")

            # Always place relative to the parent container
            target_widget = getattr(container, "widget", container)

            # Extract high-level options
            x = eff_opts.pop("x", None)
            y = eff_opts.pop("y", None)
            w = eff_opts.pop("width", None)
            h = eff_opts.pop("height", None)
            xoff = int(eff_opts.pop("xoffset", 0) or 0)
            yoff = int(eff_opts.pop("yoffset", 0) or 0)

            place_kwargs: dict[str, Any] = {}

            # x → relx/x with optional xoffset
            if x is not None:
                xv, xpct = parse_dim(x)  # returns (value, is_relative)
                if xpct:
                    place_kwargs["relx"] = xv
                    if xoff:
                        place_kwargs["x"] = xoff
                else:
                    place_kwargs["x"] = int(xv) + xoff
            elif xoff:
                place_kwargs["x"] = xoff

            # y → rely/y with optional yoffset
            if y is not None:
                yv, ypct = parse_dim(y)
                if ypct:
                    place_kwargs["rely"] = yv
                    if yoff:
                        place_kwargs["y"] = yoff
                else:
                    place_kwargs["y"] = int(yv) + yoff
            elif yoff:
                place_kwargs["y"] = yoff

            # width/height → relwidth/relheight or width/height
            if w is not None:
                wv, wpct = parse_dim(w)
                place_kwargs["relwidth" if wpct else "width"] = wv

            if h is not None:
                hv, hpct = parse_dim(h)
                place_kwargs["relheight" if hpct else "height"] = hv

            # Pass through only the native place extras you allow
            if "anchor" in eff_opts:
                place_kwargs["anchor"] = eff_opts["anchor"]
            if "bordermode" in eff_opts:
                place_kwargs["bordermode"] = eff_opts["bordermode"]

            # Execute
            self.widget.place(in_=target_widget, **place_kwargs)
            return self

        if m_eff == "widget":
            # Child executes by asking the parent to accept it as a “widget child”
            if hasattr(container, "add"):
                container.add(self, **eff_opts)
            else:
                raise RuntimeError(
                    "Parent does not support widget-style attach "
                    "(implement add(child, **opts))."
                )
            return self

        raise RuntimeError(f"Unknown layout method: {m_eff}")

    # --------------------------- Helpers ------------------------------
    def _resolve_container(self) -> Widget:
        container = getattr(self, "parent", None)
        if container is None and has_current_container():
            container = current_container()
        if container is None:
            raise RuntimeError("No active layout container; use a container context or pass parent=...")
        return container

    def _infer_layout_method(self, container: Widget | None = None) -> LayoutMethod:
        c = container or getattr(self, "parent", None) or (current_container() if has_current_container() else None)

        root_like = c is not None and str(getattr(c, "widget", c)) == "."
        if root_like:
            return "pack"

        if c is not None and hasattr(c, "preferred_layout_method"):
            try:
                pm = c.preferred_layout_method()
                if pm in ("grid", "pack", "place", "widget"):
                    return pm  # type: ignore[return-value]
            except Exception:
                pass

        name = type(c).__name__.lower() if c is not None else ""
        if c is not None and hasattr(c, "guide_layout"):
            try:
                pm = c.preferred_layout_method()
                if pm in ("grid", "pack", "place", "widget"):
                    return pm  # type: ignore[return-value]
            except Exception:
                pass
        if "grid" in name:
            return "grid"
        if "pack" in name:
            return "pack"
        if name in ("notebook", "panedwindow"):
            return "widget"
        return "grid"

    # ---------------------- Visibility / lifecycle ---------------------
    def hide(self) -> Self:
        """Un-manage the widget but keep the saved layout for a future empty attach()."""
        mgr = self.widget.winfo_manager()
        if mgr == "grid":
            self.widget.grid_remove()  # Tk preserves grid config
        elif mgr == "pack":
            self.widget.pack_forget()
        elif mgr == "place":
            self.widget.place_forget()
        return self

    def detach(self) -> Self:
        """Un-manage the widget and forget the saved layout."""
        mgr = self.widget.winfo_manager()
        if mgr == "grid":
            self.widget.grid_forget()
        elif mgr == "pack":
            self.widget.pack_forget()
        elif mgr == "place":
            self.widget.place_forget()
        # forget saved layout
        self.__layout_saved = None
        if hasattr(self, "_saved_layout"):
            setattr(self, "_saved_layout", None)
        return self
