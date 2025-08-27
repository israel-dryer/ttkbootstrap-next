from __future__ import annotations

from typing import Any, Literal, Tuple, Unpack, Self

from ttkbootstrap.exceptions import LayoutError
from ttkbootstrap.common.types import (
    GridItemOptions,
    PackItemOptions,
    PlaceItemOptions,
    Widget,
    Position, Primitive,
)
from ttkbootstrap.core.layout_context import current_container, has_current_container
from ttkbootstrap.common.utils import assert_valid_keys, parse_dim

LayoutMethod = Literal["grid", "pack", "place"]


class LayoutMixin:
    """
    Layout semantics:
      - layout(...): describe only. Stores (method, options) on the widget; never mounts.
      - attach(...): may accept kwargs (override or merge) and mounts via the active container.

    Method inference:
      - If position is 'absolute' or 'fixed' -> 'place'.
      - Else container.preferred_layout_method() if available.
      - Else 'pack' when attaching directly to the root; otherwise 'grid'.
    """

    parent: Widget
    widget: Widget

    def __init__(self, *, position: Position = "static", **kwargs):
        self._position: Position = position
        self._margin = kwargs.pop("margin", 0)
        self._place_target: Widget | None = None
        self._saved_layout: Tuple[LayoutMethod, dict[str, Any]] | None = None

    # ────────────────────────── Describe ONLY ──────────────────────────
    def layout(self, method: LayoutMethod | None = None, *, merge: bool = False, **opts) -> Self:
        inferred = method or self._infer_layout_method()

        # save/merge only
        if merge and self._saved_layout and self._saved_layout[0] == inferred:
            new_opts = dict(self._saved_layout[1])
            new_opts.update(opts)
        else:
            new_opts = dict(opts)
        self._saved_layout = (inferred, new_opts)

        from ttkbootstrap.core.layout_context import has_current_container, current_container

        cont = getattr(self, "parent", None)
        if cont is None and has_current_container():
            cont = current_container()

        if cont is not None and getattr(cont, "_in_context", False):
            try:
                cont.register_layout_child(self, inferred, dict(new_opts))
            except AttributeError:
                pass

        return self

    def layout_grid(self, *, merge: bool = False, **opts: Unpack[GridItemOptions]) -> Self:
        return self.layout("grid", merge=merge, **opts)

    def layout_pack(self, *, merge: bool = False, **opts: Unpack[PackItemOptions]) -> Self:
        return self.layout("pack", merge=merge, **opts)

    def layout_place(self, *, merge: bool = False, **opts: Unpack[PlaceItemOptions]) -> Self:
        return self.layout("place", merge=merge, **opts)

    # ───────────────────────────── ATTACH ──────────────────────────────
    def attach(
            self,
            *,
            method: LayoutMethod | None = None,
            merge: bool = False,
            **options: Any,
    ) -> Self:
        """
        Mount this widget in the active container.

        Semantics:
        - If no kwargs provided, use saved layout if present; otherwise infer method and use {}.
        - If kwargs provided:
            - merge=False (default): override saved options with provided options.
            - merge=True: merge provided options into saved options (same method);
              if method changes (or none saved), provided options become the new set.
        """
        container = self._resolve_container()
        m_eff, opts_eff = self._resolve_effective_layout(
            container, explicit_method=method, merge=merge, new_opts=options
        )

        # Validate & dispatch
        if m_eff == "place":
            assert_valid_keys(opts_eff, PlaceItemOptions, where="place")
            return self._attach_place(container, **opts_eff)
        if m_eff == "pack":
            assert_valid_keys(opts_eff, PackItemOptions, where="pack")
            return self._attach_pack_like(container, opts_eff)

        # grid
        assert_valid_keys(opts_eff, GridItemOptions, where="grid")
        return self._attach_grid_like(container, opts_eff)

    # ─────────────────────────── Internals ─────────────────────────────
    def _resolve_container(self) -> Widget:
        container = getattr(self, "parent", None)
        if container is None and has_current_container():
            container = current_container()
        if container is None:
            raise RuntimeError("No active layout container; use a container context or pass parent=...")
        return container

    def _resolve_effective_layout(
            self,
            container: Widget,
            *,
            explicit_method: LayoutMethod | None,
            merge: bool,
            new_opts: dict[str, Any],
    ) -> tuple[LayoutMethod, dict[str, Any]]:
        # Decide method (explicit > saved > inferred)
        method: LayoutMethod
        if explicit_method is not None:
            method = explicit_method
        elif self._saved_layout:
            method = self._saved_layout[0]
        else:
            method = self._infer_layout_method(container)

        # Base options from saved if same method
        base_opts: dict[str, Any] = {}
        if self._saved_layout and self._saved_layout[0] == method:
            base_opts = dict(self._saved_layout[1])

        # Apply provided options per override/merge rules
        if new_opts:
            if merge and base_opts:
                eff_opts = dict(base_opts)
                eff_opts.update(new_opts)
            else:
                eff_opts = dict(new_opts)
        else:
            eff_opts = base_opts

        # Persist the effective state
        self._saved_layout = (method, dict(eff_opts))
        return method, eff_opts

    def _infer_layout_method(self, container: Widget | None = None) -> LayoutMethod:
        # Absolute/fixed positioning forces 'place'
        if self._position in ("absolute", "fixed"):
            return "place"

        c = (
                container or getattr(self, "parent", None)
                or
                (current_container() if has_current_container() else None)
        )

        # Root detection (works for raw Tk and wrappers exposing .widget)
        root_like = c is not None and str(getattr(c, "widget", c)) == "."
        if root_like:
            return "pack"

        # Ask the container, if it exposes a preference
        if c is not None and hasattr(c, "preferred_layout_method"):
            try:
                pm = c.preferred_layout_method()
                if pm in ("grid", "pack", "place"):
                    return pm  # type: ignore[return-value]
            except (LayoutError, RuntimeError, TypeError):
                # layout not ready, container mis-configured, or wrong signature
                pm = None
            if isinstance(pm, str) and pm in ("grid", "pack", "place"):
                return pm

        # Heuristics
        name = type(c).__name__.lower() if c is not None else ""
        if c is not None and (hasattr(c, "_mount_child_grid") or "grid" in name):
            return "grid"
        if c is not None and (hasattr(c, "_mount_child_pack") or "pack" in name):
            return "pack"
        return "grid"

    # ─────────────── Container adapters (pack/grid/place) ───────────────
    def _attach_pack_like(self, container: Widget, opts: dict[str, Any]) -> Self:
        # Preferred container hook
        if hasattr(container, "_mount_child_pack"):
            getattr(container, "_mount_child_pack")(self, **opts)
            return self

        # Generic .add hook (some containers implement add(...))
        if hasattr(container, "add"):
            container.add(self, **opts)
            return self

        # Root fallback
        root_like = str(getattr(container, "widget", container)) == "."
        if root_like:
            opts = dict(opts)
            opts.setdefault("fill", "both")
            opts.setdefault("expand", True)
            self._pack_on_root(self, **opts)
            return self

        raise LayoutError(
            "Parent is not managed by a layout container or root window.",
            hint="Nest children in a Grid/Pack container or call layout_* then attach().",
            code="LAYOUT_PARENT_NOT_CONTAINER",
        )

    def _attach_grid_like(self, container: Widget, opts: dict[str, Any]) -> Self:
        if hasattr(container, "_mount_child_grid"):
            getattr(container, "_mount_child_grid")(self, **opts)
            return self

        if hasattr(container, "add"):
            container.add(self, **opts)
            return self

        raise LayoutError("Container cannot mount this widget now.", code="LAYOUT_PARENT_NOT_CONTAINER")

    def _attach_place(self, container: Widget, **layout_options: Any) -> Self:
        """
        Mount with Tk 'place'.
        - 'fixed' positions relative to the toplevel (master); otherwise relative to the container.
        - Supports absolute (px) and relative (%) dimensions via parse_dim.
        """
        assert_valid_keys(layout_options, PlaceItemOptions, where="place")

        target = getattr(container, "widget", container)

        # Extract high-level dims
        x: Primitive | None = layout_options.pop("x", None)
        y: Primitive | None = layout_options.pop("y", None)
        w: Primitive | None = layout_options.pop("width", None)
        h: Primitive | None = layout_options.pop("height", None)
        xoff: int = layout_options.pop("xoffset", 0) or 0
        yoff: int = layout_options.pop("yoffset", 0) or 0

        place_kwargs: dict[str, Any] = {}

        # X
        if x is not None:
            xv, xpct = parse_dim(x)
            if xpct:
                place_kwargs["relx"] = xv
                if xoff:
                    place_kwargs["x"] = xoff
            else:
                place_kwargs["x"] = int(xv) + xoff
        elif xoff:
            place_kwargs["x"] = xoff

        # Y
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

        # Size
        if w is not None:
            wv, wpct = parse_dim(w)
            place_kwargs["relwidth" if wpct else "width"] = wv
        if h is not None:
            hv, hpct = parse_dim(h)
            place_kwargs["relheight" if hpct else "height"] = hv

        # Place relative to master for fixed; otherwise relative to container
        if self._position == "fixed" or target is self.widget.master:
            self.widget.place(**place_kwargs, **layout_options)
        else:
            self.widget.place(in_=target, **place_kwargs, **layout_options)

        return self

    # ─────────────────── Lifecycle / convenience ────────────────────────
    def detach(self) -> Self:
        if not getattr(self, "widget", None):
            return self
        mgr = self.widget.winfo_manager()
        if mgr == "grid":
            self.widget.grid_forget()
        elif mgr == "pack":
            self.widget.pack_forget()
        elif mgr == "place":
            self.widget.place_forget()
        return self

    hide = detach  # alias

    @classmethod
    def _pack_on_root(cls, widget: Widget, **options: dict[str, Any]) -> None:
        assert_valid_keys(
            options,
            PackItemOptions,
            where="pack",
            hint="The root container uses the Pack layout options",
        )
        # widget is likely a wrapper exposing .widget
        widget.widget.pack(**options)
