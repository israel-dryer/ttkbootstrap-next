from typing import TypeAlias, TypedDict, Unpack, Union, Literal
from ttkbootstrap.core.libtypes import Anchor, Fill, Side
from ttkbootstrap.widgets.layout.frame import Frame
from ttkbootstrap.core.widget import BaseWidget, layout_context_stack


class PackLayoutOptions(TypedDict, total=False):
    """
    Layout configuration options for pack-managed widgets.

    Attributes:
        side: The side of the container to pack against ('top', 'bottom', 'left', 'right').
        fill: Whether to fill space in the x and/or y direction ('x', 'y', 'both', or 'none').
        expand: Whether the widget should expand to fill any extra space.
        padx: Horizontal padding to apply (int or (left, right) tuple).
        pady: Vertical padding to apply (int or (top, bottom) tuple).
        anchor: Anchor point inside the packing space (e.g., 'center', 'n', 'sw').
        before: Pack this widget before another.
        after: Pack this widget after another.
    """
    side: Side
    fill: Fill
    expand: bool
    padx: int | tuple[int, int]
    pady: int | tuple[int, int]
    anchor: Anchor
    before: BaseWidget
    after: BaseWidget


#: A widget paired with its explicit layout options for batch addition.
WidgetWithOptions: TypeAlias = tuple[BaseWidget, PackLayoutOptions]


class PackFrame(Frame):
    """
    A container that arranges child widgets using the `pack` geometry manager,
    with support for directional layout, gap spacing, and semantic layout options.

    Attributes:
        _gap: The (horizontal, vertical) spacing between adjacent widgets.
        _direction: The logical direction of layout (row, column, etc.).
        _mounted: A mapping of managed widgets to their applied layout options.
    """

    def __init__(
            self,
            parent=None,
            gap: int | tuple[int, int] = 0,
            padding: Union[int, tuple[int, int], tuple[int, int, int, int]] = 0,
            direction: Literal["row", "row-reverse", "column", "column-reverse"] = "row",
            **kwargs
    ):
        """
        Initialize a new PackFrame layout container.

        Args:
            parent: The parent widget.
            gap: The spacing (horizontal, vertical) between packed widgets.
            padding: Internal padding around the edge of the frame.
            direction: Logical direction of layout ('row', 'column', etc.).
            **kwargs: Additional widget or layout configuration options.
        """
        super().__init__(parent, padding=padding, **kwargs)
        self._gap = self._normalize_gap(gap)
        self._direction = direction
        self._mounted: dict[BaseWidget, dict] = {}

    def __enter__(self):
        """
        Push this layout onto the layout context stack for nested layout tracking.
        """
        layout_context_stack().append(self)
        return self

    def __exit__(self, *args):
        """
        Pop this layout from the layout context stack when exiting the context.
        """
        layout_context_stack().pop()
        self.mount()

    def __lshift__(self, widget: BaseWidget):
        return self.add(widget)

    def add(self, widget: BaseWidget):
        """
        Add a single widget to this layout using its internal layout options.

        Args:
            widget: The widget to add.

        Returns:
            Self, for fluent chaining.
        """
        opts = {}

        # Determine layout side from direction if not overridden
        default_side = self._direction_to_side(self._direction)
        layout_opts = getattr(widget, "_layout_options", {})
        opts["side"] = layout_opts.get("side", default_side)

        # Padding based on direction and previous widgets
        pad_x, pad_y = self._gap
        is_horizontal = opts["side"] in ("left", "right")
        is_vertical = opts["side"] in ("top", "bottom")

        if self._mounted:
            if is_vertical:
                opts["pady"] = layout_opts.get("pady", (pad_y, 0))
            elif is_horizontal:
                opts["padx"] = layout_opts.get("padx", (pad_x, 0))
        else:
            opts["padx"] = layout_opts.get("padx", 0)
            opts["pady"] = layout_opts.get("pady", 0)

        # Forward mount with merged options
        widget.mount("pack", **opts)
        self._mounted[widget] = opts.copy()
        return self

    def add_all(self, widgets: list[BaseWidget | WidgetWithOptions]):
        """
        Add multiple widgets to the layout at once.

        Args:
            widgets: A list of widgets or (widget, options) tuples.
        """
        for item in widgets:
            if isinstance(item, tuple):
                widget, opts = item
                widget._layout_options = opts
                self.add(widget)
            else:
                self.add(item)

    def remove(self, widget: BaseWidget):
        """
        Remove a widget from the layout and forget its pack geometry.

        Args:
            widget: The widget to remove.
        """
        if widget in self._mounted:
            widget.widget.pack_forget()
            del self._mounted[widget]

    def configure_child(self, widget: BaseWidget, option: str = None, **options: Unpack[PackLayoutOptions]):
        """
        Update layout options for a managed child and re-apply its layout.

        Args:
            widget: The child widget to reconfigure.
            option: If provided, returns the current value for this key instead of updating.
            **options: Updated layout options.

        Returns:
            Self, or the current option value if `option` is provided.

        Raises:
            ValueError: If the widget is not managed by this layout.
        """
        if widget not in self._mounted:
            raise ValueError("Widget is not managed by this layout.")

        if option:
            return self._mounted[widget].get(option)

        widget._layout_options.update(options)
        self.remove(widget)
        self.add(widget)
        return self

    @staticmethod
    def _normalize_gap(gap: int | tuple[int, int]) -> tuple[int, int]:
        """
        Normalize the gap to a (horizontal, vertical) tuple.

        Args:
            gap: A single int or a tuple of two ints.

        Returns:
            A tuple representing (pad_x, pad_y).
        """
        if isinstance(gap, int):
            return gap, gap
        return gap

    @staticmethod
    def _direction_to_side(direction: str) -> Side:
        """
        Convert a logical direction into a Tkinter pack side.

        Args:
            direction: One of 'row', 'row-reverse', 'column', 'column-reverse'.

        Returns:
            A string representing the pack side: 'left', 'right', 'top', or 'bottom'.
        """
        match direction:
            case "row":
                return "left"
            case "column":
                return "top"
            case "row-reverse":
                return "right"
            case _:
                return "bottom"
