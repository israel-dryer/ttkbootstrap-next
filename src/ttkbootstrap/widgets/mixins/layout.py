from typing import overload, Unpack, TypeVar

from ttkbootstrap.core.widget import BaseWidget
from ttkbootstrap.widgets.layout.grid_layout import GridLayout, GridLayoutOptions
from ttkbootstrap.widgets.layout.pack_layout import PackLayout, PackLayoutOptions

T = TypeVar("T", bound="BaseWidget")


class LayoutMixin:
    """
    Mixin that adds a unified `.mount()` method to declaratively add the widget
    to its parent layout container (e.g., GridLayout, PackLayout) using typed layout options.

    Example:
        Button(parent, ...).mount(row=0, col=1)
        Entry(parent, ...).mount(side="left", expand=True)
    """

    parent: BaseWidget

    @overload
    def mount(self: T, **kwargs: Unpack[GridLayoutOptions]) -> T:
        """Grid Layout"""
        ...

    @overload
    def mount(self: T, **kwargs: Unpack[PackLayoutOptions]) -> T:
        """Pack Layout"""
        ...

    def mount(self: T, **kwargs) -> T:
        """Mount this widget into its layout container using the given options."""

        if isinstance(self.parent, GridLayout):
            parent.add(self, **kwargs)  # type: ignore

        elif isinstance(self.parent, PackLayout):
            self.parent.add(self, **kwargs)  # type: ignore

        else:
            raise TypeError("Unsupported layout container.")

        return self
