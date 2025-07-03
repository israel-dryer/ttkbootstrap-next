from typing import Literal, Union, TypedDict

BindScopeType = Literal['all', 'class', 'widget']
TraceOperationType = Literal["array", "read", "write", "unset"]

ColorShadeType = Literal[100, 200, 300, 400, 500, 600, 700, 800, 900]
ColorThemeType = Union[Literal['light', 'dark'], str]
ColorModelType = Literal['hex', 'hsl', 'rgb']
ButtonSizeType = Literal['sm', 'md', 'lg']


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


