from typing import Union, Unpack

from ttkbootstrap.style.types import SemanticColor
from ttkbootstrap.utils import merge_build_options
from ttkbootstrap.widgets import Label
from ttkbootstrap.widgets.badge.style import BadgeStyleBuilder
from ttkbootstrap.widgets.badge.types import BadgeOptions, BadgeVariant


class Badge(Label):
    """A label styled as a badge."""

    def __init__(
            self,
            text: str = "",
            color: SemanticColor = "primary",
            variant: Union[BadgeVariant, str] = "default",
            **kwargs: Unpack[BadgeOptions]
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
        build_options = merge_build_options(
            kwargs.pop('builder', {}),
            color=color,
            variant=variant
        )
        # override the label style builder
        super().__init__(text, font='label', **kwargs)
        self._style_builder = BadgeStyleBuilder(**build_options)
