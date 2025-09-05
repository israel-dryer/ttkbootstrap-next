from __future__ import annotations

import tkinter as tk
from typing import Callable, Literal, Optional, TypedDict, Union, Tuple
from PIL.ImageTk import PhotoImage

BindScope = Literal['all', 'class', 'widget']
TraceOperation = Literal["array", "read", "write", "unset"]
Variable = Union["Signal", "Variable", str]
Widget = Union["BaseWidget", "App", tk.Misc, tk.Widget]
Image = Union["BootstrapIcon", "LucideIcon", PhotoImage]
Orientation = Literal["horizontal", "vertical"]
Number = Union[int, float]
Primitive = Union[Number, str]

# Other
Compound = Literal['text', 'image', 'center', 'top', 'bottom', 'left', 'right', 'none']
IconPosition = Optional[Literal["start", "end", "top", "bottom", "center", "auto"]]
ScrollCommand = Callable[[str, str], None]

# Layout
Position = Literal["static", "fixed", "absolute"]
LayoutMethod = Literal['pack', 'grid', 'place']
Fill = Literal['x', 'y', 'both', 'none']
Side = Literal['left', 'right', 'top', 'center', 'bottom']
Sticky = Union[Literal['n', 'e', 's', 'w', 'ns', 'ew', 'nsew', ''], str]
Margin = int | tuple[int, int] | tuple[int, int, int, int]
Direction = Literal["row", "row-reverse", "column", "column-reverse"]
Anchor = Literal['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'center']
Padding = Union[int, Tuple[int, int], Tuple[int, int, int, int]]
Justify = Literal['left', 'center', 'right']
JustifyLayout = Literal["left", "center", "right", "stretch"]
AlignLayout = Literal["top", "center", "bottom", "stretch"]
Spacing = Union[int, tuple[int, int]]
Gap = Spacing


class GridItemOptions(TypedDict, total=False):
    row: int
    column: int
    rowspan: int
    columnspan: int
    sticky: Sticky
    anchor: Anchor
    marginx: Spacing
    marginy: Spacing


class PackItemOptions(TypedDict, total=False):
    side: Side
    fill: Fill
    expand: bool
    anchor: Anchor
    before: Widget
    after: Widget
    marginx: Spacing
    marginy: Spacing


class PlaceItemOptions(TypedDict, total=False):
    x: int | float | str
    y: int | float | str
    width: int | float | str
    height: int | float | str
    anchor: Anchor
    bordermode: Literal["inside", "outside"]
    target: Widget
    xoffset: int
    yoffset: int


class CoreOptions(TypedDict, total=False):
    parent: Widget
    position: Position


class LayoutOpts(GridItemOptions, PackItemOptions, PlaceItemOptions):
    pass
