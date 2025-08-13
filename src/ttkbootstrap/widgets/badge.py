from typing import Literal, Union

from ttkbootstrap.layouts.constants import current_layout
from ttkbootstrap.style.builders.badge import BadgeStyleBuilder
from ttkbootstrap.style.tokens import SemanticColor
from ttkbootstrap.widgets.label import Label


class Badge(Label):
    """A label styled as a badge."""

    def __init__(
            self,
            parent=None,
            text: str = "",
            color: SemanticColor = "primary",
            variant: Union[Literal['default', 'pill', 'circle'], str] = "default",
            **kwargs
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
        parent = parent or current_layout()
        build_options = kwargs.pop('builder', dict())
        super().__init__(parent, text, font='label')
        # override the label style builder
        self._style_builder = BadgeStyleBuilder(color, variant, **build_options)
        self.update_style()
