from typing import Literal, Tuple, TypedDict, Union

from ttkbootstrap.types import Anchor, CoreOptions, Justify, ScrollCommand

CanvasTagOrId = Union[int, str]


class CanvasOptions(CoreOptions, total=False):
    """
    Configuration options for a Canvas widget, including both standard Tk options and canvas-specific settings.

    Attributes:
        background: Background color of the canvas.
        border_width: Width of the border around the canvas.
        cursor: Mouse cursor to display when over the canvas.
        highlight_background: Color of the highlight when the canvas does not have focus.
        highlight_color: Color of the highlight when the canvas has focus.
        highlight_thickness: Thickness of the highlight border.
        insert_background: Color of the insertion cursor (for text items).
        insert_border_width: Width of the insertion cursor's border.
        insert_off_time: Time in milliseconds the insertion cursor is off during blink.
        insert_on_time: Time in milliseconds the insertion cursor is on during blink.
        insert_width: Width of the insertion cursor.
        relief: Type of border decoration. One of: 'flat', 'raised', 'sunken', 'groove', or 'ridge'.
        select_background: Background color of selected text (for text items).
        select_border_width: Width of the border around selected text.
        select_foreground: Foreground color of selected text.
        take_focus: Determines if the canvas accepts focus during tab traversal.
        xscroll_command: Function to call with horizontal scrollbar parameters.
        yscroll_command: Function to call with vertical scrollbar parameters.
        close_enough: Distance (float) within which mouse events are considered to hit items.
        confine: If True, canvas view is confined to the scroll_region.
        height: Height of the canvas in pixels.
        scroll_region: Bounding box (x1, y1, x2, y2) defining the scrollable area of the canvas.
        state: Canvas state; either 'normal' (active) or 'disabled'.
        width: Width of the canvas in pixels.
        xscroll_increment: Step size for horizontal scrolling in pixels.
        yscroll_increment: Step size for vertical scrolling in pixels.
    """

    # Standard widget options
    background: str
    bg: str  # alias
    border_width: int
    bd: int  # alias
    cursor: str
    highlight_background: str
    highlight_color: str
    highlight_thickness: int
    insert_background: str
    insert_border_width: int
    insert_off_time: int
    insert_on_time: int
    insert_width: int
    relief: str
    select_background: str
    select_border_width: int
    select_foreground: str
    take_focus: Union[bool, str]
    yscroll_command: ScrollCommand
    xscroll_command: ScrollCommand

    # Canvas-specific options
    close_enough: float
    confine: bool
    height: int
    scroll_region: Union[str, tuple[int, int, int, int]]
    state: Literal['normal', 'disabled']
    width: int
    xscroll_increment: int
    yscroll_increment: int


class StandardCanvasItemOptions(TypedDict, total=False):
    """
    Common styling options for all canvas items, including fill,
    outline, state, tags, dash patterns, and stipple effects.
    """
    fill: str
    outline: str
    width: float

    active_fill: str
    disabled_fill: str
    active_outline: str
    disabled_outline: str
    active_width: float
    disabled_width: float

    dash: Union[int, Tuple[int, ...], str]
    active_dash: Union[int, Tuple[int, ...], str]
    disabled_dash: Union[int, Tuple[int, ...], str]
    dash_offset: float
    stipple: str
    active_stipple: str
    disabled_stipple: str
    outline_stipple: str
    active_outline_stipple: str
    disabled_outline_stipple: str

    tags: Union[str, Tuple[str, ...]]
    state: Literal["normal", "hidden", "disabled"]

    offset: Union[int, str]
    outline_offset: float


class CanvasArcOptions(StandardCanvasItemOptions, total=False):
    """
    Canvas arc options including start angle, extent, and style.
    Inherits standard canvas item styling.
    """
    start: float
    extent: float
    style: Literal["pieslice", "chord", "arc"]


class CanvasLineOptions(StandardCanvasItemOptions, total=False):
    """
    Canvas line options including smoothing, cap/join style,
    and spline interpolation steps.
    """
    cap_style: Literal["butt", "projecting", "round"]
    join_style: Literal["round", "bevel", "miter"]
    smooth: Union[bool, int]
    spline_steps: int


class CanvasTextOptions(StandardCanvasItemOptions, total=False):
    """
    Canvas text options including content, font, justification,
    angle, and anchor positioning.
    """
    text: str
    anchor: Anchor
    font: Union[str, Tuple[str, int], Tuple[str, int, str]]
    justify: Justify
    angle: float


class CanvasRectangleOptions(StandardCanvasItemOptions, total=False):
    """
    Canvas rectangle options. Inherits all standard styling.
    """
    pass


class CanvasPolygonOptions(StandardCanvasItemOptions, total=False):
    """
    Canvas polygon options including smoothing and join style.
    Inherits standard canvas item styling.
    """
    smooth: bool
    spline_steps: int
    join_style: Literal["round", "bevel", "miter"]


class CanvasImageOptions(TypedDict, total=False):
    """
    Canvas image options for positioning, state, and tagging.
    """
    anchor: Anchor
    tags: Union[str, Tuple[str, ...]]
    state: Literal["normal", "hidden", "disabled"]


class CanvasWidgetOptions(TypedDict, total=False):
    """
    Canvas window options for embedding widgets with layout control.
    """
    anchor: Anchor
    width: int
    height: int
    tags: Union[str, Tuple[str, ...]]
    state: Literal["normal", "hidden", "disabled"]


class CanvasOvalOptions(StandardCanvasItemOptions, total=False):
    """
    Canvas oval options. Inherits all standard styling properties
    such as fill, outline, width, and dash patterns.
    """
    pass


CanvasTextIndex = Union[int, Literal["insert", "end", "sel.first", "sel.last"]]
CanvasItemOptions = Union[
    CanvasArcOptions,
    CanvasRectangleOptions,
    CanvasOvalOptions,
    CanvasLineOptions,
    CanvasPolygonOptions,
    CanvasTextOptions,
    CanvasImageOptions,
    CanvasWidgetOptions,
]
