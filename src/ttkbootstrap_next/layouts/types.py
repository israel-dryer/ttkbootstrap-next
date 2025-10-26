from __future__ import annotations

from typing import Literal, TypedDict

from ttkbootstrap_next.types import Anchor, Fill, Padding, Position, Side, Spacing, Sticky, Widget


class FrameOptions(TypedDict, total=False):
    """Optional keyword arguments accepted by the `Frame` widget.

    Attributes:
        cursor: Mouse cursor to display when hovering over the frame.
        height: The height of the frame in pixels.
        padding: Space around the frame content.
        take_focus: Specifies if the frame accepts focus during keyboard traversal.
        width: The width of the frame in pixels.
        builder: key-value options passed to the style builder
        border: The border color.
    """
    cursor: str
    height: int
    padding: Padding
    take_focus: bool
    width: int
    builder: dict
    parent: Widget
    position: Position
    border: str | bool


class GridOptions(FrameOptions, total=False):
    surface: str
    variant: str


class GridItemOptions(TypedDict, total=False):
    row: int
    column: int
    rowspan: int
    columnspan: int
    sticky: Sticky
    anchor: Anchor
    padx: Spacing
    pady: Spacing
    ipadx: int | float
    ipady: int | float


class PackItemOptions(TypedDict, total=False):
    side: Side
    fill: Fill
    expand: bool
    anchor: Anchor
    before: Widget
    after: Widget
    padx: Spacing
    pady: Spacing
    ipadx: int | float
    ipady: int | float


class PlaceItemOptions(TypedDict, total=False):
    x: int | float | str
    y: int | float | str
    width: int | float | str
    height: int | float | str
    anchor: Anchor
    bordermode: Literal["inside", "outside"]
    xoffset: int
    yoffset: int


class LayoutOpts(GridItemOptions, PackItemOptions, PlaceItemOptions):
    pass
