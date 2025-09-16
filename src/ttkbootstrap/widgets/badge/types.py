from typing import Literal

from ttkbootstrap.types import Anchor, CoreOptions, Justify, Padding

BadgeVariant = Literal['default', 'pill', 'circle']


class BadgeOptions(CoreOptions, total=False):
    """Optional keyword arguments accepted by the `Badge` widget.

    Attributes:
        anchor: Specifies how the information in the widget is positioned relative to the inner margins.
        cursor: Mouse cursor to display when hovering over the label.
        justify: Specifies how the lines are laid out relative to one another with multiple lines of text.
        padding: Space around the label content.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        underline: The integer index (0-based) of a character to underline in the text.
        width: The width of the widget in pixels.
        wrap_length: The maximum line length in pixels.
        builder: key-value options passed to the style builder
    """
    anchor: Anchor
    cursor: str
    justify: Justify
    padding: Padding
    take_focus: bool
    underline: int
    width: int
    wrap_length: int
    builder: dict
