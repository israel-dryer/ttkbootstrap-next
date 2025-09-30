from typing import TypedDict

from ttkbootstrap.types import CoreOptions, Variable


class SwitchChangedData(TypedDict):
    checked: bool
    value: int | str
    prev_value: int | str


class SwitchInvokeData(TypedDict):
    checked: bool
    value: int | str


class SwitchOptions(CoreOptions, total=False):
    """Optional keyword arguments accepted by the `Switch` widget.

    Attributes:
        cursor: Mouse cursor to display when hovering over the widget.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
        underline: The integer index (0-based) of a character to underline in the text.
        width: The width of the widget in pixels.
        parent: The parent of this widget.
    """
    cursor: str
    take_focus: bool
    underline: int
    width: int
    variable: Variable
