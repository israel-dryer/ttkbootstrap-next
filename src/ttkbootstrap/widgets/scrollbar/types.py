from typing import Callable

from ttkbootstrap.types import CoreOptions


class ScrollbarOptions(CoreOptions, total=False):
    """
    Options for configuring a scrollbar widget.

    Attributes:
        command: The `xview` or `yview` method of a scrollable widget
        cursor: The cursor that appears when the mouse is over the widget.
        id: A unique identifier used to query this widget.
        parent: The parent container of this widget.
        position: The `place` container position.
        take_focus: Indicates whether the widget accepts focus during keyboard traversal.
    """
    cursor: str
    take_focus: bool
    command: Callable
