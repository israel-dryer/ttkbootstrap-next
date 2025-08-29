from ttkbootstrap.types import PackItemOptions, Side, Padding, Fill, Anchor, PlaceItemOptions
from ttkbootstrap.utils import assert_valid_keys
from ttkbootstrap.core.layout_context import push_container, pop_container
from ttkbootstrap.layouts.base_layout import BaseLayout, FrameOptions
from ttkbootstrap.layouts.utils import add_pad
from typing import Optional, Literal, Unpack, cast, Any, List, Tuple
import tkinter as tk
from tkinter import ttk


class PackOptions(FrameOptions, total=False):
    surface: str
    variant: str


class Pack(BaseLayout):
    widget: ttk.Frame

    def __init__(
            self,
            *,
            direction: Literal["horizontal", "vertical", "row", "column", "row-reverse", "column-reverse"] = "vertical",
            gap: int = 0,
            padding: Padding = 0,
            propagate: Optional[bool] = None,
            expand_items: Optional[bool] = None,
            fill_items: Optional[Fill] = None,
            anchor_items: Optional[Anchor] = None,
            **kwargs: Unpack[PackOptions]
    ):
        """Create a stack-like container that arranges children with Tk's `pack`.

        The container orients its children via `direction`, applies a container-level
        `gap` between siblings (only after the first child), and sets optional
        item-level defaults (`expand_items`, `fill_items`, `anchor_items`) that are
        used when a child omits those options at attach time.

        Args:
            direction: Logical orientation of the stack; "top/bottom/left/right".
            gap: Pixel spacing between adjacent children (applied after the first).
            padding: Inner padding of the container (int or `(x, y)`).
            propagate: If set, toggles `pack_propagate` on the underlying frame.
            expand_items: Default `expand` for children that don't specify one.
            fill_items: Default `fill` for children that don't specify one.
            anchor_items: Default `anchor` for children that don't specify one.
            **kwargs: Additional options.
        """
        super().__init__(**kwargs)
        self._direction = direction
        self._gap = gap
        self._padding = padding
        self._propagate = propagate
        self._expand_items = expand_items
        self._fill_items = fill_items
        self._anchor_items = anchor_items

        self._side_map = {
            "vertical": "top",
            "column": "top",
            "column-reverse": "bottom",
            "horizontal": "left",
            "row": "left",
            "row-reverse": "right"
        }
        if self._propagate is not None:
            self.widget.pack_propagate(self._propagate)
        self.widget.configure(padding=self._padding)

        # queue + context flag: store (child, method, opts)
        self._layout_children: List[Tuple[Any, str, dict]] = []
        self._in_context: bool = False

    # context mgmt
    def __enter__(self):
        """Enter layout context; attach self and push as current container."""
        self._in_context = True
        push_container(self)
        self.attach()
        return self

    def __exit__(self, exc_type, exc, tb):
        """Flush queued children and pop this container from the context."""
        try:
            self._mount_queued_children()
        finally:
            self._in_context = False
            pop_container()

    def register_layout_child(self, child, method: str, opts: dict):
        """Validate and upsert a child record for 'pack'/'place'; queues only."""
        if method not in ("pack", "place"):
            return
        if method == "pack":
            assert_valid_keys(opts, PackItemOptions, where="pack")
        else:
            assert_valid_keys(opts, PlaceItemOptions, where="place")
        for i, (c, m, _) in enumerate(self._layout_children):
            if c is child:
                self._layout_children[i] = (child, method, dict(opts))
                break
        else:
            self._layout_children.append((child, method, dict(opts)))

    def add(self, child, **options: Unpack[PackItemOptions]):
        """Queue or update a child with pack options; mounts now if not in context."""
        pack_options = dict(**options)
        assert_valid_keys(pack_options, PackItemOptions, where="pack")
        if not pack_options and hasattr(child, "_saved_layout") and (saved_layout := getattr(child, "_saved_layout")):
            m, saved = saved_layout
            if m == "pack":
                pack_options = dict(saved)
        # upsert
        for i, (c, m, _) in enumerate(self._layout_children):
            if c is child and m == "pack":
                self._layout_children[i] = (child, "pack", pack_options)
                break
        else:
            self._layout_children.append((child, "pack", pack_options))
        if not self._in_context:
            self._mount_queued_children()

    # drain queue
    def _mount_queued_children(self):
        """Drain the queue and mount children in FIFO order."""
        while self._layout_children:
            child, method, opts = self._layout_children.pop(0)
            if method == "pack":
                self._mount_child_pack(child, **opts)
            elif method == "place":
                self._mount_child_place(child, opts)

    # realization
    def _mount_child_pack(self, child, **options: Unpack[PackItemOptions]):
        """Apply gap/margins/defaults and call widget.pack(**options)."""
        pack_options: dict[str, Any] = dict(**options)
        widget = getattr(child, "widget", child)
        side = pack_options.get("side", None)
        if side not in ("top", "bottom", "left", "right", "center"):
            side = cast(Side, self._side_map.get(self._direction, "top"))

        siblings = [c for c in self.widget.winfo_children() if isinstance(c, tk.Widget)]
        is_first = len(siblings) == 0

        # Apply directional gap (only for non-first siblings)
        if not is_first:
            if self._direction in ("vertical", "column"):
                pack_options.setdefault("pady", (self._gap, 0))
            elif self._direction == "column-reverse":
                pack_options.setdefault("pady", (0, self._gap))
            elif self._direction in ("horizontal", "row"):
                pack_options.setdefault("padx", (self._gap, 0))
            elif self._direction == "row-reverse":
                pack_options.setdefault("padx", (0, self._gap))

        # --- apply marginx/marginy as external padding ---
        mx = pack_options.pop("marginx", None) or 0
        my = pack_options.pop("marginy", None) or 0

        pack_options["padx"] = add_pad(pack_options.get("padx"), mx)
        pack_options["pady"] = add_pad(pack_options.get("pady"), my)

        padx = pack_options.get("padx", None) or 0
        pady = pack_options.get("pady", None) or 0
        pack_options["padx"] = add_pad(padx, mx)
        pack_options["pady"] = add_pad(pady, my)

        # Apply item-level defaults
        if self._expand_items is not None:
            pack_options.setdefault("expand", self._expand_items)
        if self._fill_items is not None:
            pack_options.setdefault("fill", self._fill_items)
        if self._anchor_items is not None:
            pack_options.setdefault("anchor", self._anchor_items)

        pack_options.setdefault('side', side)
        widget.pack(**pack_options)

    def preferred_layout_method(self) -> str:
        """Return the container’s preferred layout method ('pack')."""
        return "pack"
