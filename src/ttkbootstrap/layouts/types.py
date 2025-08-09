from __future__ import annotations

from typing import Literal, Union, Tuple, TypedDict

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


class SemanticLayoutOptions(TypedDict, total=False):
    sticky: Sticky
    expand: bool
    padding: Padding
    margin: Margin
    row: int
    column: int
    rowspan: int
    colspan: int


