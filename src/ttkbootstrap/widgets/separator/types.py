from typing import Literal, Union

from ttkbootstrap.style.types import SemanticColor
from ttkbootstrap.types import CoreOptions

SeparatorColor = Union[Literal['border'], SemanticColor]


class SeparatorOptions(CoreOptions, total=False): ...
