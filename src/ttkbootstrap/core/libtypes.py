from typing import Literal, Union, TypedDict, TYPE_CHECKING, Tuple

from ttkbootstrap.core.widget import BaseWidget

if TYPE_CHECKING:
    from tkinter import PhotoImage, Variable
    from ttkbootstrap.icons import BootstrapIcon, LucideIcon
    from ttkbootstrap.core.signal import Signal
    from ttkbootstrap.core.app import App
    from tkinter import Misc

BindScope = Literal['all', 'class', 'widget']
TraceOperation = Literal["array", "read", "write", "unset"]
VariableType = Union["Signal", "Variable", str]
Anchor = Literal['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'center']
LabelAnchor = Literal['nw', 'n', 'ne', 'en', 'es', 'se', 's', 'sw', 'ws', 'w', 'wn']
ColorShade = Literal[100, 200, 300, 400, 500, 600, 700, 800, 900]
ColorMode = Union[Literal['light', 'dark'], str]
ColorModel = Literal['hex', 'hsl', 'rgb']
ButtonSize = Literal['sm', 'md', 'lg']
Justify = Literal['left', 'center', 'right']
Orient = Literal['horizontal', 'vertical']
ImageType = Union["PhotoImage", "BootstrapIcon", "LucideIcon"]
Padding = Union[int, Tuple[int, int], Tuple[int, int, int, int]]
Compound = Literal['text', 'image', 'center', 'top', 'bottom', 'left', 'right', 'none']
WidgetType = Union["BaseWidget", "App", "Misc"]


## Cursor https://www.tcl-lang.org/man/tcl8.6/TkCmd/cursors.htm

class ButtonOptions(TypedDict, total=False):
    """
    Defines the optional keyword arguments accepted by the `Button` widget.

    Attributes:
        default: Used to set the button that is designated as "default"; in a dialog for example.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        underline: The integer index (0-based) of a character to underline in the text.
        width: The width of the widget in pixels.
    """
    default: Literal['normal', 'active', 'disabled']
    take_focus: bool
    underline: int
    width: int


class FrameOptions(TypedDict, total=False):
    """Optional keyword arguments accepted by the `Frame` widget.

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
    orient: Orient
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
