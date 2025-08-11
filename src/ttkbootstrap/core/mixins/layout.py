"""
ttkbootstrap.layout_mixin
=========================

Lightweight layout/stacking helpers used by ttkbootstrap widgets.

Key features
------------
- **Per-parent stacking context** managed by a private `_StackManager` that lives
  on the *actual Tk container* a widget is mapped into.
- **z-index support** via the layout dictionary: set `layout["zindex"]` when
  constructing a widget, or call `widget.zindex(n)` afterwards.
- **Deterministic ordering**: items **without** an explicit z-index are
  considered *implicit* and are always lifted **below** any explicit items.
  Implicit siblings keep a stable creation order.
- **Automatic registration**: `LayoutMixin` binds `<Map>`, `<Unmap>`, and
  `<Destroy>` so widgets are (un)registered as they appear/disappear.
  If you need the correct stacking *immediately* after a synchronous geometry
  call (e.g., right after `_auto_mount()`), call
  `self._register_and_maybe_sync(force_sync=True)` once.
- **Place() extensions**: accepts percentage strings for `x/y/width/height`,
  translates `border_mode` → `bordermode`, and allows explicit `container`.

Scope & limitations
-------------------
- Stacking is **per Tk parent** (sibling scope). A child cannot out-stack
  a sibling from another container; raise the container instead if needed.
- Tk doesn’t expose child stacking directly; we enforce the desired order by
  calling `.lift()` in bottom→top sequence.
"""

from __future__ import annotations
from typing import Any, Literal, TYPE_CHECKING, TypedDict, Unpack
from tkinter import ttk

if TYPE_CHECKING:
    from ttkbootstrap.core.base_widget_alt import BaseWidget


# =============================================================================
# Internal per-parent stack manager
# =============================================================================
class _StackManager:
    """
    Maintain a stacking context for a single Tk container.

    Policy:
      - Children with **no explicit z-index** (implicit) are kept in a stable
        creation order (tracked by a monotonic sequence) and always sit **below**
        any explicit children.
      - Children with an **explicit z-index** are ordered by that integer; higher
        numbers end up visually on top because we lift bottom→top.

    Implementation notes:
      - We don't inspect Tk's internal child stack. Instead we compute the
        desired order and enforce it by `widget.lift()` from bottom to top.
      - Registration happens per *actual* container (the widget returned by
        `winfo_parent()`), which covers grid/pack/place and any custom
        "content" frames used by containers.
    """
    __slots__ = ("parent_tk", "z_implicit", "z_explicit", "_seq", "_dirty")

    def __init__(self, parent_tk):
        """
        Args:
            parent_tk: The Tk container (e.g., a Frame) this manager governs.
        """
        self.parent_tk = parent_tk
        self.z_implicit: dict[Any, int] = {}  # widget -> creation sequence
        self.z_explicit: dict[Any, int] = {}  # widget -> explicit zindex
        self._seq = 0
        self._dirty = False

    # ---- registry ops ----
    def register(self, widget, zindex: int | None = None):
        """
        Add/update a child in this stacking context.

        Args:
            widget: The Tk widget to manage.
            zindex: If None, the child is implicit (ordered by creation seq).
                    Otherwise, set as explicit z-index.
        """
        if zindex is None:
            self.z_implicit[widget] = self._seq
            self._seq += 1
            self.z_explicit.pop(widget, None)
        else:
            self.z_explicit[widget] = int(zindex)
            self.z_implicit.pop(widget, None)
        self._dirty = True
        self._gc()

    def set_zindex(self, widget, zindex: int):
        """
        Make/keep the child explicit and set its z-index.

        Args:
            widget: Child widget.
            zindex: Integer z-index (higher paints later/topmost).
        """
        self.z_explicit[widget] = int(zindex)
        self.z_implicit.pop(widget, None)
        self._dirty = True

    def get_zindex(self, widget) -> int | None:
        """
        Returns:
            The explicit z-index if the child is explicit, else None (implicit).
        """
        return self.z_explicit.get(widget)

    # ---- syncing ----
    def _desired_order(self) -> list[Any]:
        """
        Compute bottom→top order: implicit (by seq), then explicit (by zindex).
        """
        implicit = [w for w, _ in sorted(self.z_implicit.items(), key=lambda kv: kv[1])]
        explicit = [w for w, _ in sorted(self.z_explicit.items(), key=lambda kv: kv[1])]
        return implicit + explicit  # bottom→top

    def needs_sync(self) -> bool:
        """Return True if registration/indices changed since last sync()."""
        return self._dirty

    def sync(self) -> None:
        """
        Enforce desired stacking by lifting children from bottom→top.
        The last lifted child is the topmost.
        """
        if not self._dirty:
            return
        for w in self._desired_order():
            try:
                w.lift()
            except Exception:
                # Ignore disposed children.
                pass
        self._dirty = False
        self._gc()

    def unregister(self, widget) -> None:
        """
        Remove a child from this context. Safe to call on already-removed widgets.
        """
        changed = (
                self.z_implicit.pop(widget, None) is not None
                or self.z_explicit.pop(widget, None) is not None
        )
        if changed:
            self._dirty = True

    def _gc(self) -> None:
        """Drop dead widget references from internal maps."""
        for d in (self.z_implicit, self.z_explicit):
            for w in list(d):
                if not str(w):  # Tk returns empty string for destroyed widgets
                    d.pop(w, None)


def _get_stack_manager(parent_obj) -> _StackManager | None:
    """
    Get or lazily attach the `_StackManager` for the given parent.

    The manager is stored on the Tk container as `.__stack_manager__`.

    Args:
        parent_obj: A BaseWidget-like (with `.widget`) or a raw Tk container.

    Returns:
        The `_StackManager` instance for that container, or None if unavailable.
    """
    if parent_obj is None:
        return None
    tk_parent = getattr(parent_obj, "widget", parent_obj)
    if not hasattr(tk_parent, "__stack_manager__"):
        try:
            tk_parent.__stack_manager__ = _StackManager(tk_parent)
        except Exception:
            return None
    return tk_parent.__stack_manager__


# =============================================================================
# Public API
# =============================================================================
class PlacePositionOptions(TypedDict, total=False):
    """Additional, friendlier options supported by `LayoutMixin.place()`.

    Keys:
        x, y: int pixels or str percent (e.g., "50%") → maps to `x`/`relx`, `y`/`rely`.
        width, height: int pixels or str percent (e.g., "25%") → `width`/`relwidth`, `height`/`relheight`.
        anchor: Tk anchor string ("n", "sw", etc.).
        border_mode: "inside" | "outside" → translated to Tk's `bordermode`.
        container: optional BaseWidget or raw Tk widget to use as `in_` target.
    """
    x: int | str
    y: int | str
    width: int | str
    height: int | str
    anchor: str
    border_mode: Literal["inside", "outside"]
    container: "BaseWidget"


class LayoutMixin:
    """
    Common layout helpers for ttkbootstrap widgets.

    What it adds:
      • Grid option translation for semantic keys (row/col/rowspan/colspan, margin→pad, etc.).
      • `place()` extensions:
          - percentages for x/y/width/height,
          - `container` → Tk `in_`,
          - `border_mode` → `bordermode`.
      • **z-index support**:
          - Read/write `layout["zindex"]` at construction time.
          - Runtime `.zindex()` getter/setter that re-syncs stacking.
          - Auto (un)registration on `<Map>/<Unmap>/<Destroy>`.

    Stacking policy:
      - Implicit children (no zindex) sit below any explicit ones and retain
        creation order.
      - Explicit children are ordered by integer zindex (higher → on top).

    Expectations:
      - `self.widget` is the underlying Tk widget.
      - `self.parent` is a BaseWidget-like (with `.widget`) or a raw Tk widget.
      - `self._position` is one of {'static','absolute','fixed'} set by the host.
    """
    parent: Any
    widget: Any
    _position: Literal["static", "absolute", "fixed"]

    _zindex: int | None = None  # cached explicit z-index from layout, if provided

    def __init__(self, layout: dict | None = None, **_):
        """
        Args:
            layout: Layout-related options captured from widget kwargs.
                    If present, `layout["zindex"]` seeds the stacking order.
        """
        # Track only what you need for geometry; include zindex here.
        self._layout_options: dict[str, Any] = layout.copy() if layout else {}
        self._zindex = int(self._layout_options["zindex"]) if "zindex" in self._layout_options else None

        # Auto (un)registration around mapping lifecycle.
        if hasattr(self, "widget") and self.widget is not None:
            try:
                # Register when the widget is mapped; unregister when unmapped/destroyed.
                self.widget.bind("<Map>", lambda e: self._register_and_maybe_sync(force_sync=True))
                self.widget.bind("<Unmap>", lambda e: self._unregister_from_stack())
                self.widget.bind("<Destroy>", lambda e: self._unregister_from_stack(), add=True)
            except Exception:
                pass

    # --------------------- public zindex api ---------------------
    def zindex(self, value: int | None = None) -> int | None:
        """
        Get or set the explicit z-index for this widget.

        - **Getter**: returns the explicit z-index if set, else None (implicit).
        - **Setter**: writes the value into `layout["zindex"]`, updates the
          cached `_zindex`, and re-syncs the parent stacking context.

        Args:
            value: Optional integer. If omitted, acts as a getter.

        Returns:
            The explicit z-index (getter) or the value just set (setter).
        """
        mgr = _get_stack_manager(getattr(self, "parent", None))
        if value is None:
            if self._zindex is not None:
                return self._zindex
            return mgr.get_zindex(self.widget) if mgr else None

        self._zindex = int(value)
        self._layout_options["zindex"] = self._zindex
        self._register_and_maybe_sync(force_sync=True)
        return self._zindex

    # --------------------- mounting helpers ---------------------
    def _auto_mount(self) -> None:
        """
        Mount this widget:

        - If `position != 'static'`, the caller is manually placing the widget.
        - Else, if the parent exposes `add(self)`, delegate to the parent layout.
        - Otherwise, default to `grid` via `mount()`.

        Note: If you require immediate stacking correctness in the same tick
        (before `<Map>` fires), call `_register_and_maybe_sync(force_sync=True)`
        right after invoking `_auto_mount()` from the host class.
        """
        if self._position != "static":
            return  # user is placing this widget manually
        if getattr(self.parent, "add", None):
            self.parent.add(self)
        else:
            self.mount()  # grid by default

    def mount(self, **overrides):
        """
        Grid-mount this widget using translated layout options.

        Args:
            **overrides: Any final `grid()` keyword args to override translation.

        Returns:
            self
        """
        opts = self._translate_grid_layout(self._layout_options.copy())
        opts.update(overrides)
        self.widget.grid(**opts)
        return self

    def place(self, **kwargs: Unpack[PlacePositionOptions]):
        """
        Place this widget using Tk's `place()` with a friendlier API.

        Extensions:
          - Percent strings for `x`, `y`, `width`, and `height` (e.g., `"50%"`).
          - `container` (BaseWidget or raw Tk) → translated to `in_`.
          - `border_mode` (`"inside"` or `"outside"`) → translated to `bordermode`.

        Returns:
            self
        """
        container = kwargs.pop("container", None)
        border_mode = kwargs.pop("border_mode", None)

        options = LayoutMixin._translate_place_options(**kwargs)
        options |= self._identify_place_container(container)
        if border_mode is not None:
            options["bordermode"] = border_mode

        self.widget.place(**options)
        return self

    # --------------------- stacking plumbing ---------------------
    def _resolve_actual_container(self, fallback=None):
        """
        Resolve the *actual* Tk container this widget is mapped into.

        Tkinter containers sometimes use internal content frames. Registering
        against the wrong parent (logical wrapper instead of actual container)
        would make `.lift()` ineffective.

        Args:
            fallback: A BaseWidget/raw Tk to use if `winfo_parent()` is unavailable.

        Returns:
            The raw Tk container that currently owns this widget.
        """
        try:
            pname = self.widget.winfo_parent()
            return self.widget.nametowidget(pname)
        except Exception:
            return getattr(fallback, "widget", fallback)

    def _register_and_maybe_sync(self, *, container=None, force_sync: bool = False) -> None:
        """
        Register this widget in its container's stacking context and, if needed,
        enforce the desired order.

        Args:
            container: Optional BaseWidget/raw Tk container to override resolution.
            force_sync: If True, always call `sync()` after registering.
        """
        tk_container = self._resolve_actual_container(
            fallback=container or getattr(self, "parent", None)
        )
        if not tk_container:
            return
        mgr = _get_stack_manager(tk_container)
        mgr.register(self.widget, self._zindex)
        if force_sync or mgr.needs_sync():
            mgr.sync()

    def _unregister_from_stack(self) -> None:
        """Unregister this widget from its parent's stacking context, if present."""
        parent = getattr(self, "parent", None)
        mgr = _get_stack_manager(parent)
        if mgr:
            mgr.unregister(self.widget)

    # ---------------------- option plumbing ---------------------
    @staticmethod
    def layout_from_options(kwargs: dict[str, Any] | None) -> dict:
        """
        Extract layout/geometry options from widget kwargs.

        Recognized keys:
            sticky, margin, padding,
            row, col/column, rowspan, colspan, offset,
            padx, pady, ipadx, ipady, expand,
            zindex

        Returns:
            A new dict with recognized keys removed from `kwargs`.
        """
        if not kwargs:
            return {}
        layout: dict[str, Any] = {}
        for k in (
                "sticky", "margin", "padding",
                # grid placement
                "row", "col", "column", "rowspan", "colspan", "offset",
                # direct geometry overrides
                "padx", "pady", "ipadx", "ipady", "expand",
                # stacking
                "zindex",
        ):
            if k in kwargs:
                layout[k] = kwargs.pop(k)
        return layout

    # --------------------- grid translation ---------------------
    def _translate_grid_layout(self, layout: dict) -> dict:
        """
        Translate semantic layout options to `grid()` kwargs.

        - Accepts `col` or `column`.
        - Maps `margin` → `padx/pady` (supports int, (x,y), or (l,t,r,b)).
        - For non-`ttk.Frame` widgets, maps `padding` → `ipadx/ipady`.

        Args:
            layout: Semantic layout options.

        Returns:
            Dict of Tk grid options.
        """
        opts: dict[str, Any] = {}

        # sticky passes through
        if layout.get("sticky"):
            opts["sticky"] = layout["sticky"]

        # placement (accept both 'col' and 'column')
        if "row" in layout:
            opts["row"] = layout["row"]
        if "col" in layout:
            opts["column"] = layout["col"]
        elif "column" in layout:
            opts["column"] = layout["column"]
        if "rowspan" in layout:
            opts["rowspan"] = layout["rowspan"]
        if "colspan" in layout:
            opts["columnspan"] = layout["colspan"]

        # margin -> outer padding
        margin: list | int = layout.get("margin", 0)
        if isinstance(margin, int):
            opts["padx"] = margin
            opts["pady"] = margin
        elif isinstance(margin, tuple):
            if len(margin) == 2:
                opts["padx"], opts["pady"] = margin
            elif len(margin) == 4:
                l, t, r, b = margin
                opts["padx"] = (l, r)
                opts["pady"] = (t, b)

        # padding -> internal space for non-Frame widgets
        pad: list | int = layout.get("padding", 0)
        if not isinstance(self.widget, ttk.Frame):
            if isinstance(pad, int):
                opts["ipadx"] = pad
                opts["ipady"] = pad
            elif isinstance(pad, tuple) and len(pad) == 2:
                opts["ipadx"], opts["ipady"] = pad

        # explicit geometry overrides
        for k in ("padx", "pady", "ipadx", "ipady"):
            if k in layout:
                opts[k] = layout[k]

        return opts

    # --------------------- place translation helpers ---------------------
    @staticmethod
    def _relative_value(key, value):
        """Translate an int pixel or '%'-string into Tk absolute or relative key."""
        if isinstance(value, int):
            return {key: value}
        else:
            return {f"rel{key}": float(value.replace("%", "")) / 100}

    @staticmethod
    def _translate_place_options(**kwargs) -> dict[str, Any]:
        """
        Convert friendly place kwargs into Tk's `place_configure()` keys,
        handling percent values for position/size.
        """
        opts = kwargs.copy()

        def rel(key, value):
            if isinstance(value, int):
                return {key: value}
            # Expect strings like "75%"
            return {f"rel{key}": float(value.replace("%", "")) / 100.0}

        if "width" in opts:
            v = opts.pop("width")
            opts |= rel("width", v)
        if "height" in opts:
            v = opts.pop("height")
            opts |= rel("height", v)
        if "x" in opts:
            v = opts.pop("x")
            opts |= rel("x", v)
        if "y" in opts:
            v = opts.pop("y")
            opts |= rel("y", v)
        return opts

    def _identify_place_container(self, container):
        """
        Resolve Tk's `in_` target for `place()`.

        Args:
            container: BaseWidget or raw Tk container. If None, use:
                - toplevel for `position == "fixed"`,
                - `self.parent` otherwise.

        Returns:
            Dict containing the `in_` key for `place()` (or empty if not needed).
        """
        # Use explicit container if provided
        if container is not None:
            # Accept either a BaseWidget or a Tk widget
            try:
                tk_container = getattr(container, "widget", container)
            except Exception:
                tk_container = container
            return {"in_": tk_container}

        # Otherwise decide by position mode
        if getattr(self, "_position", "static") == "fixed":
            # Use the actual toplevel, not the literal "."
            return {"in_": self.widget.winfo_toplevel()}
        else:
            return {"in_": getattr(self, "parent", None)}
