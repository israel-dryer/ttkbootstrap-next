from typing import Literal, TypedDict

from ttkbootstrap.types import CoreOptions, Orientation

class ProgressbarChangedData(TypedDict):
    value: float
    prev_value: float

class ProgressbarOptions(CoreOptions, total=False):
    """
    Options for configuring a progress bar widget.

    Attributes:
        cursor: The cursor that appears when the mouse is over the widget.
        take_focus: Indicates whether the widget accepts focus during keyboard traversal.
        length: The length of the progress bar in pixels.
        maximum: The maximum value for the progress bar range.
        orient: Indicates whether the widget should be laid or horizontally or vertically
        mode: Use 'determinate' for measurable progress and 'indeterminate' for continuous animation.
        parent: The parent widget for this widget.
    """
    cursor: str
    take_focus: bool
    length: int
    maximum: float
    orient: Orientation
    mode: Literal['determinate', 'indeterminate']
