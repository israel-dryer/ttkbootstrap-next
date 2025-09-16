from __future__ import annotations
from typing import Any, Literal, Tuple, Unpack, Self

from ttkbootstrap.exceptions import LayoutError
from ttkbootstrap.types import (
    Widget, Position, Primitive,
)
from ttkbootstrap.layouts.types import GridItemOptions, PackItemOptions, PlaceItemOptions
from ttkbootstrap.core.layout_context import current_container, has_current_container
from ttkbootstrap.utils import assert_valid_keys, parse_dim

LayoutMethod = Literal["grid", "pack", "place", "widget"]


class LayoutMixin:
    """
    Layout semantics:
      - layout(...): describe only. Stores (method, options) on the widget; never mounts.
      - attach(...): may accept kwargs (override or merge) and mounts via the active container.
    """

    parent: Widget
    widget: Widget

    # public-ish fields kept for compatibility
    _position: Position
    _margin: Any

    # name-mangled, collision-proof internals
    __layout_place_target: Widget | None
    __layout_saved: Tuple[LayoutMethod, dict[str, Any]] | None

    def __init__(self, *args, position: Position = "static", **kwargs):
        # consume mixin-specific kwargs
        margin = kwargs.pop("margin", 0)
        super().__init__(*args, **kwargs)  # cooperative MI

        # keep compatibility fields
        self._position = position
        self._margin = margin

        # internal state
        self.__layout_place_target = None
        self.__layout_saved = None

    # Friendly accessor going forward; existing code can still use _position
    @property
    def position(self) -> Position:
        return self._position

    @position.setter
    def position(self, value: Position) -> None:
        self._position = value

    # ────────────────────────── Describe ONLY ──────────────────────────
    def layout(self, method: LayoutMethod | None = None, *, merge: bool = False, **opts) -> Self:
        inferred = method or self._infer_layout_method()

        if merge and self.__layout_saved and self.__layout_saved[0] == inferred:
            new_opts = dict(self.__layout_saved[1]);
            new_opts.update(opts)
        else:
            new_opts = dict(opts)
        self.__layout_saved = (inferred, new_opts)

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
    def attach(self, *, method: LayoutMethod | None = None, merge: bool = False, **options: Any) -> Self:
        container = self._resolve_container()
        m_eff, opts_eff = self._resolve_effective_layout(
            container, explicit_method=method, merge=merge, new_opts=options
        )
        if m_eff == "place":
            assert_valid_keys(opts_eff, PlaceItemOptions, where="place")
            return self._attach_place(container, **opts_eff)
        if m_eff == "pack":
            assert_valid_keys(opts_eff, PackItemOptions, where="pack")
            return self._attach_pack_like(container, opts_eff)
        if m_eff == "widget":
            return self._attach_widget_like(container, opts_eff)
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
            self, container: Widget, *, explicit_method: LayoutMethod | None, merge: bool, new_opts: dict[str, Any],
    ) -> tuple[LayoutMethod, dict[str, Any]]:
        if explicit_method is not None:
            method: LayoutMethod = explicit_method
        elif self.__layout_saved:
            method = self.__layout_saved[0]
        else:
            method = self._infer_layout_method(container)

        base_opts: dict[str, Any] = {}
        if self.__layout_saved and self.__layout_saved[0] == method:
            base_opts = dict(self.__layout_saved[1])

        if new_opts:
            eff_opts = dict(base_opts);
            eff_opts.update(new_opts) if (merge and base_opts) else None
            if not (merge and base_opts): eff_opts = dict(new_opts)
        else:
            eff_opts = base_opts

        self.__layout_saved = (method, dict(eff_opts))
        return method, eff_opts

    def _infer_layout_method(self, container: Widget | None = None) -> LayoutMethod:
        # respect fixed/absolute
        if self.position in ("absolute", "fixed"):
            return "place"

        c = container or getattr(self, "parent", None) or (current_container() if has_current_container() else None)

        root_like = c is not None and str(getattr(c, "widget", c)) == "."
        if root_like:
            return "pack"

        if c is not None and hasattr(c, "preferred_layout_method"):
            try:
                pm = c.preferred_layout_method()
                if pm in ("grid", "pack", "place", "widget"):
                    return pm  # type: ignore[return-value]
            except (LayoutError, RuntimeError, TypeError):
                pm = None
            if isinstance(pm, str) and pm in ("grid", "pack", "place"):
                return pm

        name = type(c).__name__.lower() if c is not None else ""
        if c is not None and (hasattr(c, "_mount_child_grid") or "grid" in name):
            return "grid"
        if c is not None and (hasattr(c, "_mount_child_pack") or "pack" in name):
            return "pack"
        if name in ("notebook", "panedwindow"):
            return "widget"
        return "grid"

    # ─────────────── Container adapters (pack/grid/place) ───────────────
    def _attach_widget_like(self, container: Widget, opts: dict[str, Any]) -> Self:
        if hasattr(container, "_validate_options"):
            getattr(container, "_validate_options")(opts)
        container.add(self, **opts)
        return self

    def _attach_pack_like(self, container: Widget, opts: dict[str, Any]) -> Self:
        if hasattr(container, "_mount_child_pack"):
            getattr(container, "_mount_child_pack")(self, **opts)
            return self
        if hasattr(container, "add"):
            container.add(self, **opts)
            return self
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
        assert_valid_keys(layout_options, PlaceItemOptions, where="place")
        target = getattr(container, "widget", container)

        x: Primitive | None = layout_options.pop("x", None)
        y: Primitive | None = layout_options.pop("y", None)
        w: Primitive | None = layout_options.pop("width", None)
        h: Primitive | None = layout_options.pop("height", None)
        xoff: int = layout_options.pop("xoffset", 0) or 0
        yoff: int = layout_options.pop("yoffset", 0) or 0

        place_kwargs: dict[str, Any] = {}

        if x is not None:
            xv, xpct = parse_dim(x)
            if xpct:
                place_kwargs["relx"] = xv
                if xoff: place_kwargs["x"] = xoff
            else:
                place_kwargs["x"] = int(xv) + xoff
        elif xoff:
            place_kwargs["x"] = xoff

        if y is not None:
            yv, ypct = parse_dim(y)
            if ypct:
                place_kwargs["rely"] = yv
                if yoff: place_kwargs["y"] = yoff
            else:
                place_kwargs["y"] = int(yv) + yoff
        elif yoff:
            place_kwargs["y"] = yoff

        if w is not None:
            wv, wpct = parse_dim(w)
            place_kwargs["relwidth" if wpct else "width"] = wv
        if h is not None:
            hv, hpct = parse_dim(h)
            place_kwargs["relheight" if hpct else "height"] = hv

        target_widget = target
        if self.position == "fixed" or target_widget is self.widget.master:
            self.widget.place(**place_kwargs, **layout_options)
        else:
            self.widget.place(in_=target_widget, **place_kwargs, **layout_options)
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
    def _pack_on_root(cls, widget: Widget, **options: Any) -> None:
        assert_valid_keys(options, PackItemOptions, where="pack")
        widget.widget.pack(**options)
