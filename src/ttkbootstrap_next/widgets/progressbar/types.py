from tkinter import Variable
from typing import Literal, TypedDict

from ttkbootstrap_next.types import CoreOptions, Orientation


class ProgressbarChangedData(TypedDict):
    value: float
    prev_value: float


class ProgressbarOptions(CoreOptions, total=False):
    """
    Options for configuring a progress bar widget.

    Attributes:
        cursor: The cursor that appears when the mouse is over the widget.
        id: A unique identifier used to query this widget.
        length: The length of the progress bar in pixels.
        maximum: The maximum value for the progress bar range.
        mode: Use 'determinate' for measurable progress and 'indeterminate' for continuous animation.
        orient: Indicates whether the widget should be laid or horizontally or vertically.
        parent: The parent container of this widget.
        take_focus: Indicates whether the widget accepts focus during keyboard traversal.
        variable: The tkinter variable linked to this widget's value.
    """
    cursor: str
    take_focus: bool
    length: int
    maximum: float
    orient: Orientation
    mode: Literal['determinate', 'indeterminate']
    variable: Variable
