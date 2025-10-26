from typing import Literal, Union

from ttkbootstrap_next.style.types import SemanticColor
from ttkbootstrap_next.types import CoreOptions

SeparatorColor = Union[Literal['border'], SemanticColor]


class SeparatorOptions(CoreOptions, total=False):
    """
        Attributes:
            parent: The parent container of this widget.
            id: A unique identifier used to query this widget.
    """
    ...
