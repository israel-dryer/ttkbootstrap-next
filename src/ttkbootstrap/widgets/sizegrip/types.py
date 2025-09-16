from ttkbootstrap.types import CoreOptions


class SizegripOptions(CoreOptions, total=False):
    """Optional keyword arguments accepted by the `SizeGrip` widget.

    Attributes:
        cursor: Mouse cursor to display when hovering over the widget.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
    """
    cursor: str
    take_focus: bool
