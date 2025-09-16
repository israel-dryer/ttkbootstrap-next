from typing import TypedDict

from ttkbootstrap.types import CoreOptions, Orientation


class ScaleOptions(CoreOptions, total=False):
    """
    Options for configuring a slider widget.

    Attributes:
        cursor: The cursor that appears when the mouse is over the widget.
        take_focus: Indicates whether the widget accepts focus during keyboard traversal.
        length: The length of the progress bar in pixels.
        orient: Indicates whether the widget should be laid or horizontally or vertically
    """
    cursor: str
    take_focus: bool
    length: int
    orient: Orientation


class ScaleChangedData(TypedDict):
    value: int | float
    prev_value: int | float
