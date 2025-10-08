from tkinter import StringVar
from typing import TypedDict

from ttkbootstrap.types import CoreOptions, Variable


class RadiobuttonChangedData(TypedDict):
    selected: bool
    value: int | str
    prev_value: int | str


class RadiobuttonInvokeData(TypedDict):
    selected: bool
    value: int | str


class RadiobuttonOptions(CoreOptions, total=False):
    """Optional keyword arguments accepted by the `Radiobutton` widget.

    Attributes:
        cursor: Mouse cursor to display when hovering over the widget.
        id: A unique identifier used to query this widget.
        parent: The parent container of this widget.
        position: The `place` container position.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        text_variable: The tkinter text variable bound to the widget label.
        underline: The integer index (0-based) of a character to underline in the text.
        variable: The tkinter variable bound to the widget value.
        width: The width of the widget in pixels.
    """
    cursor: str
    take_focus: bool
    underline: int
    width: int
    variable: Variable
    text_variable: StringVar
