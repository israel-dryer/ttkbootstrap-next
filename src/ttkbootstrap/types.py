from __future__ import annotations

import tkinter as tk
from typing import Any, Callable, Literal, Mapping, Optional, Protocol, Tuple, TypeVar, TypedDict, Union, \
    runtime_checkable

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


class CoreOptions(TypedDict, total=False):
    """Optional keyword arguments accepted by all widgets.

    Attributes:
        parent: The parent container of this widget.
        position: The `place` container position.
        id: A unique identifier used to lookup this widget.
    """
    parent: Widget
    position: Position
    id: str


AltEventHandler = Union[Callable[[], Any], Callable[[Any], Any]]
EventHandler = Callable[[Any], Any]

TData = TypeVar("TData", bound=Mapping[str, Any])


@runtime_checkable
class UIEvent(Protocol[TData]):
    name: str
    target: str | None
    timestamp: str | None
    toplevel: str | None
    data: TData
