from typing import TypeAlias, TypedDict, Unpack, Union

from ttkbootstrap.core.libtypes import Anchor, Fill, Side
from ttkbootstrap.widgets.layout.frame import Frame
from ttkbootstrap.core.widget import BaseWidget, layout_context_stack


class PackLayoutOptions(TypedDict, total=False):
    """Layout configuration options for pack-managed widgets."""
    side: Side
    fill: Fill
    expand: bool
    padx: int | tuple[int, int]
    pady: int | tuple[int, int]
    anchor: Anchor
    before: BaseWidget
    after: BaseWidget


WidgetWithOptions: TypeAlias = tuple[BaseWidget, PackLayoutOptions]


class PackLayout(Frame):
    """
    A layout container using the Tkinter pack geometry manager with added support
    for gap and default layout options.

    This layout component simplifies stacking widgets horizontally or vertically
    with consistent spacing, padding, and alignment. Global layout options such as
    side, fill, expand, and anchor can be configured once on the container and will
    be used as defaults for each child added.

    Args:
        parent: The parent widget.
        gap: Gap between widgets in pixels or (x, y) tuple.
        padding: Internal padding for the container.
        side: Default side to pack widgets ('top', 'left', etc.).
        fill: Default fill behavior ('x', 'y', 'both', 'none').
        expand: Whether children should expand into extra space by default.
        anchor: Default anchor alignment within available space.
        **kwargs: Additional keyword arguments passed to the Frame constructor.
    """

    def __init__(
            self,
            parent = None,
            gap: int | tuple[int, int] = 0,
            padding: Union[int, tuple[int, int], tuple[int, int, int, int]] = 0,
            side: Side = "left",
            fill: Fill = "none",
            expand: bool = False,
            anchor: Anchor = "center",
            **kwargs
    ):
        super().__init__(parent, padding=padding, **kwargs)
        self._gap = self._normalize_gap(gap)
        self._side = side
        self._anchor = anchor
        self._fill = fill
        self._expand = expand
        self._mounted: dict[BaseWidget, dict] = {}

    def __enter__(self):
        layout_context_stack().append(self)
        return self

    def __exit__(self, *args):
        layout_context_stack().pop()

    def add(self, widget: BaseWidget, **options: Unpack[PackLayoutOptions]):
        """Add a widget to the layout using optional layout overrides."""
        side = options.setdefault("side", self._side)
        options.setdefault("anchor", self._anchor)
        options.setdefault("expand", self._expand)
        options.setdefault("fill", self._fill)

        pad_x, pad_y = self._gap
        is_horizontal = side in ("left", "right")
        is_vertical = side in ("top", "bottom")

        if self._mounted:
            if is_vertical:
                options.setdefault("pady", (pad_y, 0))
            elif is_horizontal:
                options.setdefault("padx", (pad_x, 0))
        else:
            options.setdefault("padx", 0)
            options.setdefault("pady", 0)

        widget.pack(**options)
        self._mounted[widget] = options.copy()
        return self

    def add_all(self, widgets: list[BaseWidget | WidgetWithOptions]):
        """Add a sequence of widgets with optional layout configurations."""
        for item in widgets:
            if isinstance(item, tuple):
                widget, opts = item
                self.add(widget, **opts)
            else:
                self.add(item)

    def remove(self, widget: BaseWidget):
        """Remove a widget from the layout."""
        if widget in self._mounted:
            widget.widget.pack_forget()
            del self._mounted[widget]

    def configure_child(
            self,
            widget: BaseWidget,
            option: str = None,
            **options: Unpack[PackLayoutOptions]
    ):
        """Reconfigure a managed child widget's layout options.

        Args:
            widget: The child widget to update.
            option: If set, return the current value for this option.
            **options: New layout options to apply to the widget.

        Returns:
            The option value if `option` is provided, or self.
        """
        if widget not in self._mounted:
            raise ValueError("Widget is not managed by this layout.")

        if option:
            return self._mounted[widget].get(option)

        self.remove(widget)
        self.add(widget, **options)
        return self

    @staticmethod
    def _normalize_gap(gap: int | tuple[int, int]) -> tuple[int, int]:
        """Normalize gap to a (x, y) tuple."""
        if isinstance(gap, int):
            return gap, gap
        return gap
