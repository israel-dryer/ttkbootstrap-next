from typing import Literal, Union, Unpack

from ttkbootstrap.style.builders.badge import BadgeStyleBuilder
from ttkbootstrap.style.types import SemanticColor
from ttkbootstrap.widgets.label import Label, LabelOptions


class Badge(Label):
    """A label styled as a badge."""

    def __init__(
            self,
            text: str = "",
            color: SemanticColor = "primary",
            variant: Union[Literal['default', 'pill', 'circle'], str] = "default",
            **kwargs: Unpack[LabelOptions]
    ):
        """
        Initialize a Badge widget.

        Args:
            text:
                The text displayed inside the badge.
            color:
                The badge color, selected from the semantic theme palette.
                Defaults to "primary".
            variant:
                The badge shape variant. Choose from:
                - "default": Standard rectangular shape.
                - "pill": Rounded ends.
                - "circle": Circular shape.
        """
        build_options = kwargs.pop('builder', dict())
        super().__init__(text, font='label', **kwargs)
        # override the label style builder
        self._style_builder = BadgeStyleBuilder(color, variant, **build_options)
