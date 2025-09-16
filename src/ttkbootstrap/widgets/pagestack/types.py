from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal, Protocol, TypedDict, Union

from ttkbootstrap.types import Anchor, CoreOptions, Fill, Gap, Padding, Sticky


class PageStackOptions(CoreOptions, total=False):
    """Configuration options for the PageStack container."""
    take_focus: bool
    width: int
    height: int
    padding: Padding


class PageOptions(TypedDict, total=False):
    """Options that can be configured per-page within a PageStack."""
    name: str
    state: Literal['normal', 'disabled', 'hidden']
    sticky: Sticky
    padding: Padding


class GridPageOptions(TypedDict, total=False):
    """Typed options for configuring a GridPage."""
    rows: Union[int, list[Union[int, str]]]
    columns: Union[int, list[Union[int, str]]]
    gap: Gap
    padding: Padding
    sticky_items: Sticky
    propagate: bool
    auto_flow: Literal['row', 'column', 'dense-row', 'dense-column', 'none']
    surface: str
    variant: str


class PackPageOptions(TypedDict, total=False):
    """Typed options for configuring a PackPage."""
    direction: Literal["horizontal", "vertical", "row", "column", "row-reverse", "column-reverse"]
    gap: int
    padding: Padding
    propagate: bool
    expand_items: bool
    fill_items: Fill
    anchor_items: Anchor
    surface: str
    variant: str


class PageEventHandler(Protocol):
    def __call__(self, event: Any) -> Any: ...


Page = Union["GridPage", "PackPage"]


class Nav(StrEnum):
    PUSH = "push"
    REPLACE = "replace"
    BACK = "back"
    FORWARD = "forward"


class NavigationData(TypedDict):
    page: str
    prev_page: str
    prev_data: "NavigationData"
    nav: Nav
    length: int
    can_back: bool
    can_forward: bool
