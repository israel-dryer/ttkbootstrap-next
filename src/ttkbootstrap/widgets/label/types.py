from __future__ import annotations

import tkinter

from ttkbootstrap.types import Anchor, Compound, CoreOptions, Image, Justify, Padding


class LabelOptions(CoreOptions, total=False):
    """Optional keyword arguments accepted by the `Label` widget.

    Attributes:
        anchor: Specifies how the information in the widget is positioned relative to the inner margins.
        builder: Key-value options passed to the style builder.
        compound: Specifies the relative position of the image and text.
        cursor: Mouse cursor to display when hovering over the label.
        image: An image to display in the label, such as a PhotoImage, BootstrapIcon, or LucideIcon.
        justify: Specifies how the lines are laid out relative to one another with multiple lines of text.
        padding: Space around the label content.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        text_variable: A tkinter variable bound to the label text.
        underline: The integer index (0-based) of a character to underline in the text.
        width: The width of the widget in pixels.
        wrap_length: The maximum line length in pixels.
    """
    anchor: Anchor
    compound: Compound
    cursor: str
    image: Image
    justify: Justify
    padding: Padding
    take_focus: bool
    underline: int
    width: int
    wrap_length: int
    builder: dict
    text_variable: tkinter.Variable
