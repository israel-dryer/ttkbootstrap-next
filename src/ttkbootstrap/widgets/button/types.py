from typing import Literal

from ttkbootstrap.types import CoreOptions, Padding


class ButtonOptions(CoreOptions, total=False):
    """
    Defines the optional keyword arguments accepted by the `Button` widget.

    Attributes:
        default: Used to set the button that is designated as "default"; in a dialog for example.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        underline: The integer index (0-based) of a character to underline in the text.
        width: The width of the widget in pixels.
        builder: key-value options passed to the style builder
        padding: The padding of the widget in pixels.
        position: Whether to use static, absolute or fixed positioning.
    """
    default: Literal['normal', 'active', 'disabled']
    cursor: str
    take_focus: bool
    underline: int
    width: int
    builder: dict
    padding: Padding


ButtonVariant = Literal['solid', 'outline', 'ghost', 'text', 'list']
ButtonSize = Literal['sm', 'md', 'lg']
