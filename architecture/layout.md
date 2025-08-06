# Layout Management

## Architecture

Currently in Tkinter, layout is specified by the child using the pack, place, grid managers. However, to make this more
modern and aligned to the bootstrap system, I'm going to be adopting the standard 12-column grid used by bootstrap, with
adjustable columns (not limited to 12). This will be the primary layout manager and will enable me to simplify layouts
and place the responsibility of layout managment of a layout component, removing it from the base widgets. Additionally,
to support a `place` type layout, there will be a `AbsoluteLayout` widget which will serve for this purpose.

## Grid Layout

The grid layout is a bootstrap inspired 12-column grid layout that enables easy column and row configuration as well as
`auto_layout`, which automatically handles the placement of columns and rows with `auto_layout`.

The columns and rows can be configured in multiple ways via the constructor. Using a single integer will designate the
number of columns equally distributed (12 by default). You can also pass in a tuple of weights or pixel sizes, where
integers are interpreted as a weight and a string is interpreted as a pixel value (e.g. `50px`). This allow for simple
configuration of complex grid layouts in the constructor. The same is true for rows, but by default, the rows are
automatically generated.

Items are adding one-by-by using the `add()` method or the `add_all()` method for bulk updates. When using the auto
layout, you can move things around when adding items to the layout by using the `offset` option, and also resize using
the `row_span` and `col_span` options.

Certain methods may be exposed on the widget itself to make things easier for tkinter users, such as `mount()`, `unmound()`, and `layout()` which call to the parent layout methods.

```python
from typing import TypedDict, Literal, Unpack
from ttkbootstrap.widgets import Frame
from ttkbootstrap.core.base_widget import BaseWidget

type Sticky = Literal['n', 'e', 's', 'w', 'ns', 'ew', 'nsew']


class GridLayoutOptions(TypedDict, total=False):
    row: int
    col: int
    row_span: int
    col_span: int
    offset: int
    sticky: Sticky
    pad_x: int | tuple[int, int]
    pad_y: int | tuple[int, int]


class GridRowOptions(TypedDict, total=False):
    weight: int
    height: int


class GridColumnOptions(TypedDict, total=False):
    weight: int
    width: int


class GridLayout(Frame):

    def __init__(
            self,
            parent,
            gap: int | tuple[int, int] = 16,  # (column_gap, row_gap)
            padding: int | tuple[int, int] | tuple[int, int, int, int] = None,
            cols: int | list[str | int] = 12,
            rows: int | list[str | int] = None,
            auto_layout=True
    ):
        self._gap = gap
        self._padding = padding
        self._cols = cols
        self._rows = rows
        self._auto_layout = auto_layout
        super().__init__(parent)

    def add(self, widget, **options: Unpack[GridLayoutOptions]):
        # expose on the widget via the `widget.mount(**options)` method?
        pass

    def remove(self, widget: BaseWidget):
        # expose on the widget via the `widget.unmount()` method
        pass

    def add_all(self, widgets: list[tuple[BaseWidget, GridLayoutOptions]]):
        pass

    def row_configure(self, index: int, **options: GridRowOptions):
        pass

    def col_configure(self, index: int, **options: GridColumnOptions):
        pass

    def child_configure(self, widget: BaseWidget, option: str = None, **options: GridLayoutOptions):
        # expose on the widget via the `widget.layout()` method?
        # should return the configuration option if requested, otherwise configure and return self
        pass

```