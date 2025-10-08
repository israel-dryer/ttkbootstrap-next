import tkinter
from typing import Literal

from ttkbootstrap.types import CoreOptions, Padding


class ButtonOptions(CoreOptions, total=False):
    """
    Defines the optional keyword arguments accepted by the `Button` widget.

    Attributes:
        default: Used to set the button that is designated as "default"; in a dialog for example.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        padding: The padding of the widget in pixels.
        position: Whether to use static, absolute or fixed positioning.
        width: The width of the widget in pixels.
        underline: The integer index (0-based) of a character to underline in the text.
        text_variable: A tkinter string variable bound to the button text.
        builder: key-value options passed to the style builder.
    """
    default: Literal['normal', 'active', 'disabled']
    cursor: str
    take_focus: bool
    underline: int
    width: int
    builder: dict
    padding: Padding
    text_variable: tkinter.StringVar


ButtonVariant = Literal['solid', 'outline', 'ghost', 'text', 'list']
ButtonSize = Literal['sm', 'md', 'lg']
