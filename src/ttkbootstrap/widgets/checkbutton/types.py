from tkinter import Variable
from typing import TypedDict

from ttkbootstrap.types import CoreOptions


class CheckbuttonChangedData(TypedDict):
    checked: bool
    value: int | str
    prev_value: int | str


class CheckbuttonInvokeData(TypedDict):
    checked: bool
    value: int | str


class CheckbuttonOptions(CoreOptions, total=False):
    """Optional keyword arguments accepted by the `Checkbutton` widget.

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
    variable: Variable
    text_variable: Variable
