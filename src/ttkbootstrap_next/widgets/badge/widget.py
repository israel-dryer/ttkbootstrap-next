from typing import Union, Unpack

from ttkbootstrap_next.style.types import SemanticColor
from ttkbootstrap_next.utils import merge_build_options
from ttkbootstrap_next.widgets.badge.style import BadgeStyleBuilder
from ttkbootstrap_next.widgets.badge.types import BadgeOptions, BadgeVariant
from ttkbootstrap_next.widgets.label import Label


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
            text: Text displayed inside the badge.
            color: Semantic color token; defaults to `"primary"`.
            variant: Badge shape variant: `"default"`, `"pill"`, or `"circle"`.
            **kwargs: Optional keyword arguments accepted by the `Badge` widget.

        Keyword Args:
            anchor: Specifies how the information in the widget is positioned relative to the inner margins.
            builder: Key-value options passed to the style builder.
            cursor: Mouse cursor to display when hovering over the label.
            id: A unique identifier used to lookup this widget.
            justify: Specifies how the lines are laid out relative to one another with multiple lines of text.
            padding: Space around the label content.
            parent: The parent container of this widget.
            take_focus: Specifies if the widget accepts focus during keyboard traversal.
            text_variable: The tkinter variable bound to this widget label text.
            underline: The integer index (0-based) of a character to underline in the text.
            width: The width of the widget in pixels.
            wrap_length: The maximum line length in pixels.
        """
        build_options = merge_build_options(kwargs.pop('builder', {}), color=color, variant=variant)
        super().__init__(text, font='label', **kwargs)
        self._style_builder = BadgeStyleBuilder(**build_options)
