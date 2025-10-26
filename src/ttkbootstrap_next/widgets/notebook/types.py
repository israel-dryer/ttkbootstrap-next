from enum import StrEnum
from typing import Literal, TypedDict, Union

from ttkbootstrap_next.types import Anchor, Compound, CoreOptions, Fill, Gap, Image, Padding, Sticky, Widget


class ChangeReason(StrEnum):
    USER = 'user'
    API = 'api'
    HIDE = 'hide'
    FORGET = 'forget'
    REORDER = 'reorder'
    UNKNOWN = 'unknown'


class ChangeMethod(StrEnum):
    CLICK = 'click'
    KEY = 'key'
    PROGRAMMATIC = 'programmatic'
    UNKNOWN = 'unknown'


class NotebookOptions(CoreOptions, total=False):
    """Options for configuring a Notebook widget.

    Attributes:
        take_focus: Accepts keyboard focus during traversal.
        width: Width of the notebook in pixels.
        height: Height of the notebook in pixels.
        id: A unique identifier used to query this widget.
        padding: Internal padding around the content area.
        parent: The parent container of this widget.
    """
    take_focus: bool
    width: int
    height: int
    padding: Padding



class NotebookTabOptions(TypedDict, total=False):
    text: str
    compound: Compound
    image: Image
    underline: int
    state: Literal['normal', 'disabled', 'hidden']


class GridTabOptions(NotebookTabOptions, total=False):
    rows: Union[int, list[Union[int, str]]]
    columns: Union[int, list[Union[int, str]]]
    gap: Gap
    padding: Padding
    sticky_items: Sticky
    propagate: bool
    auto_flow: Literal['row', 'column', 'dense-row', 'dense-column', 'none']
    surface: str
    variant: str
    parent: Widget


class PackTabOptions(NotebookTabOptions, total=False):
    direction: Literal["horizontal", "vertical", "row", "column", "row-reverse", "column-reverse"]
    gap: int
    padding: Padding
    propagate: bool
    expand_items: bool
    fill_items: Fill
    anchor_items: Anchor
    surface: str
    variant: str
    parent: Widget


class TabRef(TypedDict):
    index: int | None
    key: str | None
    label: str | None


class TabLifecycleData(TypedDict):
    tab: TabRef
    reason: ChangeReason
    via: ChangeMethod


class NotebookChangedData(TypedDict):
    current: TabRef | None
    previous: TabRef | None
    reason: ChangeReason
    via: ChangeMethod
