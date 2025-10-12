from typing import TypedDict

from ttkbootstrap.types import CoreOptions, Orientation, Variable


class ScaleOptions(CoreOptions, total=False):
    """
    Options for configuring a slider widget.

    Attributes:
        cursor: The cursor that appears when the mouse is over the widget.
        id: A unique identifier used to query this widget.
        length: The length of the progress bar in pixels.
        orient: Indicates whether the widget should be laid or horizontally or vertically.
        parent: The parent container of this widget.
        take_focus: Indicates whether the widget accepts focus during keyboard traversal.
        variable: A tkinter variable bound to the widget value.
    """
    cursor: str
    take_focus: bool
    length: int
    orient: Orientation
    variable: Variable


class ScaleChangedData(TypedDict):
    value: int | float
    prev_value: int | float
