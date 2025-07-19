from typing import Literal
from ttkbootstrap.style.builders.badge import BadgeStyleBuilder
from ttkbootstrap.style.tokens import SemanticColor
from ttkbootstrap.widgets import Label


class Badge(Label):
    """A label styled as a badge."""

    def __init__(
            self,
            parent,
            text: str,
            color: SemanticColor = "primary",
            variant: Literal['default', 'pill', 'circle'] = "default"
    ):
        """
        Initialize a Badge widget.

        Args:
            parent:
                The parent container for this widget.
            text (str):
                The text displayed inside the badge.
            color (SemanticColor, optional):
                The badge color, selected from the semantic theme palette.
                Defaults to "primary".
            variant (Literal['default', 'pill', 'circle'], optional):
                The badge shape variant. Choose from:
                - "default": Standard rectangular shape.
                - "pill": Rounded ends.
                - "circle": Circular shape.
                Defaults to "default".
        """
        super().__init__(parent, text, font='label')
        # override the label style builder
        self._style_builder = BadgeStyleBuilder(color, variant)
