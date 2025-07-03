from typing import Literal, Union, TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from ttkbootstrap.core.image import ManagedImage
    from tkinter import PhotoImage, Variable
    from ttkbootstrap.icons import BootstrapIcon, LucideIcon
    from ttkbootstrap.core.signal import Signal


BindScopeType = Literal['all', 'class', 'widget']
TraceOperationType = Literal["array", "read", "write", "unset"]
VariableType = Union["Signal", "Variable", str]

ColorShadeType = Literal[100, 200, 300, 400, 500, 600, 700, 800, 900]
ColorThemeType = Union[Literal['light', 'dark'], str]
ColorModelType = Literal['hex', 'hsl', 'rgb']
ButtonSizeType = Literal['sm', 'md', 'lg']
OrientType = Literal['horizontal', 'vertical']
ImageType = Union["PhotoImage", "BootstrapIcon", "LucideIcon"]

class ButtonOptionsType(TypedDict, total=False):
    """
    Defines the optional keyword arguments accepted by a Button widget.

    Attributes:
        default: Used to set the button that is designated as "default"; in a dialog for example.
        take_focus: Determines if the widget accepts focus during keyboard traversal.
        width: The widget of the button in pixels.
        underline: The integer index (0-based) of a character to underline in the text.
    """
    default: Literal['normal', 'active', 'disabled']
    take_focus: bool
    width: int
    underline: int

class LabelOptionsType(TypedDict, total=False):
    compound: Literal['text', 'image', 'center', 'top', 'bottom', 'left', 'right', 'none']
    cursor: str
    image: "ImageType"

