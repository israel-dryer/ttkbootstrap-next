from typing import Literal, Union, TypedDict, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from tkinter import PhotoImage, Variable
    from ttkbootstrap.icons import BootstrapIcon, LucideIcon
    from ttkbootstrap.core.signal import Signal

BindScope = Literal['all', 'class', 'widget']
TraceOperation = Literal["array", "read", "write", "unset"]
VariableType = Union[Signal, Variable, str]
Anchor = Literal['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'center']
ColorShade = Literal[100, 200, 300, 400, 500, 600, 700, 800, 900]
ColorMode = Union[Literal['light', 'dark'], str]
ColorModel = Literal['hex', 'hsl', 'rgb']
ButtonSize = Literal['sm', 'md', 'lg']
Justify = Literal['left', 'center', 'right']
Orient = Literal['horizontal', 'vertical']
ImageType = Union[PhotoImage, BootstrapIcon, LucideIcon]
Padding = Union[int, Tuple[int, int], Tuple[int, int, int, int]]
Compound = Literal['text', 'image', 'center', 'top', 'bottom', 'left', 'right', 'none']


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
        background: The widget's background color (override theme `surface`).
        compound: Specifies the relative position of the image and text.
        cursor: Mouse cursor to display when hovering over the label.
        foreground: The widget's foreground color (override theme `color`).
        image: An image to display in the label, such as a PhotoImage, BootstrapIcon, or LucideIcon.
        justify: Specifies how the lines are laid out relative to one another with multiple lines of text.
        padding: Space around the label content.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        underline: The integer index (0-based) of a character to underline in the text.
        width: The width of the widget in pixels.
        wrap_length: The maximum line length in pixels.
    """
    anchor: Anchor
    background: str
    compound: Compound
    cursor: str
    foreground: str
    image: ImageType
    justify: Justify
    padding: Padding
    take_focus: bool
    underline: int
    width: int
    wrap_length: int
