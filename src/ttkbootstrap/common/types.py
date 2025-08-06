from tkinter.font import Font
from typing import Callable, Literal, Union, TypedDict, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    pass

BindScope = Literal['all', 'class', 'widget']
Fill = Literal['x', 'y', 'both', 'none']
Side = Literal['left', 'right', 'top', 'center', 'bottom']
Sticky = Literal['n', 'e', 's', 'w', 'ns', 'ew', 'nsew', '']
TraceOperation = Literal["array", "read", "write", "unset"]
VariableType = Union["Signal", "Variable", str]
Anchor = Literal['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'center']
LabelAnchor = Literal['nw', 'n', 'ne', 'en', 'es', 'se', 's', 'sw', 'ws', 'w', 'wn']
ColorShade = Literal[100, 200, 300, 400, 500, 600, 700, 800, 900]
ColorMode = Union[Literal['light', 'dark'], str]
ColorModel = Literal['hex', 'hsl', 'rgb']
ButtonSize = Literal['sm', 'md', 'lg']
Justify = Literal['left', 'center', 'right']
JustifyLayout = Literal["left", "center", "right", "stretch"]
Margin = int | tuple[int, int] | tuple[int, int, int, int]
LayoutMethod = Literal['pack', 'grid', 'place']
AlignLayout = Literal["top", "center", "bottom", "stretch"]
Direction = Literal["row", "row-reverse", "column", "column-reverse"]
Orient = Literal['horizontal', 'vertical']
ImageType = Union["PhotoImage", "BootstrapIcon", "LucideIcon"]
Padding = Union[int, Tuple[int, int], Tuple[int, int, int, int]]
Compound = Literal['text', 'image', 'center', 'top', 'bottom', 'left', 'right', 'none']
WidgetType = Union["BaseWidget", "App", "Misc"]
ScrollCommand = Callable[[str, str], None]


## Cursor https://www.tcl-lang.org/man/tcl8.6/TkCmd/cursors.htm


class SemanticLayoutOptions(TypedDict, total=False):
    justify: JustifyLayout
    align: AlignLayout
    expand: bool
    margin: Margin
    row: int
    column: int
    rowspan: int
    colspan: int


class ButtonOptions(TypedDict, total=False):
    """
    Defines the optional keyword arguments accepted by the `Button` widget.

    Attributes:
        default: Used to set the button that is designated as "default"; in a dialog for example.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        underline: The integer index (0-based) of a character to underline in the text.
        width: The width of the widget in pixels.
        builder: key-value options passed to the style builder
    """
    default: Literal['normal', 'active', 'disabled']
    cursor: str
    take_focus: bool
    underline: int
    width: int
    builder: dict


class FrameOptions(TypedDict, total=False):
    """Optional keyword arguments accepted by the `Frame` widget.

    Attributes:
        cursor: Mouse cursor to display when hovering over the frame.
        height: The height of the frame in pixels.
        padding: Space around the frame content.
        take_focus: Specifies if the frame accepts focus during keyboard traversal.
        width: The width of the frame in pixels.
        builder: key-value options passed to the style builder
    """
    cursor: str
    height: int
    padding: Padding
    take_focus: bool
    width: int
    builder: dict


class LabelOptions(TypedDict, total=False):
    """Optional keyword arguments accepted by the `Label` widget.

    Attributes:
        anchor: Specifies how the information in the widget is positioned relative to the inner margins.
        compound: Specifies the relative position of the image and text.
        cursor: Mouse cursor to display when hovering over the label.
        image: An image to display in the label, such as a PhotoImage, BootstrapIcon, or LucideIcon.
        justify: Specifies how the lines are laid out relative to one another with multiple lines of text.
        padding: Space around the label content.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        underline: The integer index (0-based) of a character to underline in the text.
        width: The width of the widget in pixels.
        wrap_length: The maximum line length in pixels.
        builder: key-value options passed to the style builder
    """
    anchor: Anchor
    compound: Compound
    cursor: str
    image: ImageType
    justify: Justify
    padding: Padding
    take_focus: bool
    underline: int
    width: int
    wrap_length: int
    builder: dict


class LabelFrameOptions(TypedDict, total=False):
    """Optional keyword arguments accepted by the `LabelFrame` widget.

    Attributes:
        height: The height of the widget in pixels.
        label_anchor: Specifies the position of the label relative to the frame's border.
        padding: Space around the frame content.
        underline: The integer index (0-based) of a character to underline in the label text.
        width: The width of the widget in pixels.
    """
    padding: Padding
    height: int
    width: int
    label_anchor: LabelAnchor
    underline: int


class SizeGripOptions(TypedDict, total=False):
    """Optional keyword arguments accepted by the `SizeGrip` widget.

    Attributes:
        cursor: Mouse cursor to display when hovering over the widget.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
    """
    cursor: str
    take_focus: bool


class PanedWindowOptions(TypedDict, total=False):
    """Optional keyword arguments accepted by the `PanedWindow` widget.

    Attributes:
        cursor: Mouse cursor to display when hovering over the widget.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        height: The height of the widget in pixels.
        width: The width of the widget in pixels.
    """
    cursor: str
    take_focus: bool
    height: int
    width: int


class PaneOptions(TypedDict, total=False):
    """Pane configuration options for a widget managed by a PanedWindow.

    Attributes:
        after: Insert the pane after this widget (either a widget reference or widget name).
        before: Insert the pane before this widget (either a widget reference or widget name).
        height: Preferred height of the pane in pixels.
        min_size: Minimum allowed size (in pixels) for the pane in the paned dimension.
        pad_x: Horizontal padding on each side of the pane.
        pad_y: Vertical padding on each side of the pane.
        sticky: Controls how the pane widget is stretched or aligned; uses compass directions (e.g., "nsew").
        width: Preferred width of the pane in pixels.
    """
    after: Union["BaseWidget", str]
    before: Union["BaseWidget", str]
    height: int
    min_size: int
    pad_x: int
    pad_y: int
    sticky: str
    width: int


class CheckButtonOptions(TypedDict, total=False):
    """Optional keyword arguments accepted by the `CheckButton` widget.

    Attributes:
        cursor: Mouse cursor to display when hovering over the widget.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        underline: The integer index (0-based) of a character to underline in the text.
        width: The width of the widget in pixels.
    """
    cursor: str
    take_focus: bool
    underline: int
    width: int


class NotebookOptions(TypedDict, total=False):
    """Optional keyword arguments accepted by the `Notebook`` widget.

    Attributes:
        cursor: Mouse cursor to display when hovering over the frame.
        height: The height of the frame in pixels.
        padding: Space around the frame content.
        take_focus: Specifies if the frame accepts focus during keyboard traversal.
        width: The width of the frame in pixels.
    """
    cursor: str
    height: int
    padding: Padding
    take_focus: bool
    width: int


class NotebookTabOptions(TypedDict, total=False):
    """
    Defines configurable options for individual tabs in a Notebook widget.

    These options can be passed to `add()`, `insert()`, or `configure_tab()`
    to control the appearance and behavior of a specific tab.

    Attributes:
        sticky: Sticky position for the tab content (e.g., 'n', 'e', 's', 'w').
        padding: Internal padding around the tab label (e.g., 5 or (5, 10)).
        text: The text label displayed on the tab.
        image: An image displayed on the tab (e.g., PhotoImage instance).
        compound: Placement of image relative to text (e.g., 'left', 'top').
        underline: Index of character in `text` to underline for mnemonic.
    """
    sticky: str
    padding: Padding
    text: str
    image: ImageType
    compound: Compound
    underline: int


class RadioButtonOptions(TypedDict, total=False):
    """Optional keyword arguments accepted by the `RadioButton` widget.

    Attributes:
        cursor: Mouse cursor to display when hovering over the widget.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        underline: The integer index (0-based) of a character to underline in the text.
        width: The width of the widget in pixels.
    """
    cursor: str
    take_focus: bool
    underline: int
    width: int


class ProgressOptions(TypedDict, total=False):
    """
    Options for configuring a progress bar widget.

    Attributes:
        cursor: The cursor that appears when the mouse is over the widget.
        take_focus: Indicates whether the widget accepts focus during keyboard traversal.
        length: The length of the progress bar in pixels.
        maximum: The maximum value for the progress bar range.
        orient: Indicates whether the widget should be laid or horizontally or vertically
        mode: Use 'determinate' for measurable progress and 'indeterminate' for continuous animation.
    """
    cursor: str
    take_focus: bool
    length: int
    maximum: int
    orient: Orient
    mode: Literal['determinate', 'indeterminate']


class SliderOptions(TypedDict, total=False):
    """
    Options for configuring a slider widget.

    Attributes:
        cursor: The cursor that appears when the mouse is over the widget.
        take_focus: Indicates whether the widget accepts focus during keyboard traversal.
        length: The length of the progress bar in pixels.
        orient: Indicates whether the widget should be laid or horizontally or vertically
    """
    cursor: str
    take_focus: bool
    length: int
    orient: Orient


class ScrollbarOptions(TypedDict, total=False):
    """
    Options for configuring a scrollbar widget.

    Attributes:
        cursor: The cursor that appears when the mouse is over the widget.
        take_focus: Indicates whether the widget accepts focus during keyboard traversal.
        command: The `x_view` or `y_view` method of a scrollable widget
    """
    cursor: str
    take_focus: bool
    command: Callable


class EntryOptions(TypedDict, total=False):
    """
    Options for configuring an entry widget.

    Attributes:
        cursor: The cursor that appears when the mouse is over the widget.
        font: The font used to render text in the entry (name or Font object).
        foreground: The text color (e.g., "#333", "red").
        take_focus: Indicates whether the widget accepts focus during keyboard traversal.
        x_scroll_command: A callback used to link the entry to a horizontal scrollbar.
        export_selection: Whether to export the selection to the clipboard (default is True).
        justify: Text justification (left, center, or right).
        show: The character used to mask text (e.g., "*" for passwords).
        width: The width of the entry widget in characters.
    """
    cursor: str
    font: str | Font
    foreground: str
    take_focus: bool
    x_scroll_command: Callable
    export_selection: bool
    justify: Justify
    show: str
    width: int


class CanvasOptions(TypedDict, total=False):
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
        x_scroll_command: Function to call with horizontal scrollbar parameters.
        y_scroll_command: Function to call with vertical scrollbar parameters.
        close_enough: Distance (float) within which mouse events are considered to hit items.
        confine: If True, canvas view is confined to the scroll_region.
        height: Height of the canvas in pixels.
        scroll_region: Bounding box (x1, y1, x2, y2) defining the scrollable area of the canvas.
        state: Canvas state; either 'normal' (active) or 'disabled'.
        width: Width of the canvas in pixels.
        x_scroll_increment: Step size for horizontal scrolling in pixels.
        y_scroll_increment: Step size for vertical scrolling in pixels.
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
    x_scroll_command: ScrollCommand
    y_scroll_command: ScrollCommand

    # Canvas-specific options
    close_enough: float
    confine: bool
    height: int
    scroll_region: Union[str, tuple[int, int, int, int]]
    state: Literal['normal', 'disabled']
    width: int
    x_scroll_increment: int
    y_scroll_increment: int


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
