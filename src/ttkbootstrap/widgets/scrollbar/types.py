from typing import Callable

from ttkbootstrap.types import CoreOptions


class ScrollbarOptions(CoreOptions, total=False):
    """
    Options for configuring a scrollbar widget.

    Attributes:
        cursor: The cursor that appears when the mouse is over the widget.
        take_focus: Indicates whether the widget accepts focus during keyboard traversal.
    """
    cursor: str
    take_focus: bool
    on_scroll: Callable
