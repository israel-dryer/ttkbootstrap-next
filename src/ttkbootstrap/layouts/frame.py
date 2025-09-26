from typing import Literal, Unpack

from ttkbootstrap.layouts.base_layout import BaseLayout
from ttkbootstrap.layouts.types import FrameOptions

type LayoutMethod = Literal["grid", "pack", "place"]


class Frame(BaseLayout):

    def __init__(
            self, surface: str = None, variant: str = None, layout_method: LayoutMethod = "pack",
            **kwargs: Unpack[FrameOptions]):
        self._layout_method = layout_method
        super().__init__(surface=surface, variant=variant, **kwargs)

    def preferred_layout_method(self):
        return self._layout_method
