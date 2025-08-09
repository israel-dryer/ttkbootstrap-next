from __future__ import annotations
from typing import Unpack, Union, TypedDict

from ttkbootstrap.core.base_widget_alt import BaseWidget
from ttkbootstrap.layouts.frame import Frame
from ttkbootstrap.layouts.constants import layout_context_stack
from ttkbootstrap.layouts.types import Sticky, SemanticLayoutOptions
from ttkbootstrap.layouts.utils import add_pad, margin_to_pad, normalize_gap, normalize_padding
from ttkbootstrap.style.tokens import SurfaceColor
from ttkbootstrap.widgets.types import FrameOptions


class GridLayoutOptions(FrameOptions, total=False):
    row: int
    col: int
    rowspan: int
    colspan: int
    offset: int
    sticky: Sticky
    padx: int | tuple[int, int]
    pady: int | tuple[int, int]


class GridRowOptions(TypedDict, total=False):
    weight: int
    height: int


class GridColumnOptions(TypedDict, total=False):
    weight: int
    width: int


class _Options(GridLayoutOptions, SemanticLayoutOptions, total=False):
    surface: SurfaceColor
    variant: str


class GridFrame(Frame):
    def __init__(
            self,
            parent=None,
            *,
            gap: int | tuple[int, int] = 0,  # (col_gap, row_gap)
            padding: Union[int, tuple[int, int], tuple[int, int, int, int]] = 0,
            columns: int | list[str | int] = 12,
            rows: int | list[str | int] = None,
            propagate: bool = True,
            sticky_content: Sticky = None,
            expand_content: bool = None,
            **kwargs: Unpack[_Options]
    ):
        self._gap = normalize_gap(gap)
        self._padding = normalize_padding(padding)
        self._columns = columns if isinstance(columns, list) else [1] * columns
        self._rows = rows if isinstance(rows, list) else []
        self._auto_layout = True
        self._next_row = 0
        self._next_col = 0
        self._mounted: dict[BaseWidget, dict] = {}
        self._sticky_content = sticky_content
        self._expand_content = expand_content

        super().__init__(parent, padding=self._padding, **kwargs)
        self.widget.grid_propagate(propagate)

        for index, col in enumerate(self._columns):
            if isinstance(col, int):
                self.configure_column(index, weight=col)
            elif isinstance(col, str) and col.endswith("px"):
                self.configure_column(index, weight=0)
                self.widget.grid_columnconfigure(index, minsize=int(col.removesuffix("px")))

        if self._rows:
            for index, row in enumerate(self._rows):
                if isinstance(row, int):
                    self.configure_row(index, weight=row)
                elif isinstance(row, str) and row.endswith("px"):
                    self.configure_row(index, weight=0)
                    self.widget.grid_rowconfigure(index, minsize=int(row.removesuffix("px")))

    def __enter__(self):
        layout_context_stack().append(self)
        return self

    def __exit__(self, *args):
        layout_context_stack().pop()

    def add(self, widget: BaseWidget):
        layout_options = getattr(widget, "_layout_options", {}).copy()

        if self._expand_content is not None and "expand" not in layout_options:
            layout_options["expand"] = self._expand_content

        if self._sticky_content and not layout_options.get("sticky", "").strip():
            layout_options["sticky"] = self._sticky_content

        widget._layout_options = layout_options

        self._add(widget, **layout_options)

    def _add(self, widget: BaseWidget, **options: Unpack[GridLayoutOptions]):
        if self._auto_layout:
            options = self._apply_auto_layout(options)

        col = options.get("col", 0)
        row = options.get("row", 0)
        col_span = options.get("colspan", 1)
        row_span = options.get("rowspan", 1)
        sticky = options.get("sticky", "ew")

        gap_x, gap_y = self._gap

        # base gap pads centered between cells
        left_pad = gap_x // 2
        right_pad = gap_x - left_pad
        top_pad = gap_y // 2
        bottom_pad = gap_y - top_pad

        # trim outer edges
        if col == 0:
            left_pad = 0
        if (col + col_span) == len(self._columns):  # rightmost edge
            right_pad = 0
        if row == 0:
            top_pad = 0
        # bottom edge can be trimmed similarly if you know the last row length

        pad_x = (left_pad, right_pad)
        pad_y = (top_pad, bottom_pad)

        # merge margin
        margin = options.pop("margin", 0)
        m_padx, m_pady = margin_to_pad(margin)
        pad_x = add_pad(pad_x, m_padx)
        pad_y = add_pad(pad_y, m_pady)

        # merge any explicit widget-level padx/pady the child specified
        if "padx" in options:
            pad_x = add_pad(pad_x, options["padx"])
        if "pady" in options:
            pad_y = add_pad(pad_y, options["pady"])

        widget.grid(
            row=row,
            column=col,
            rowspan=row_span,
            columnspan=col_span,
            sticky=sticky,
            padx=pad_x,
            pady=pad_y,
        )

        self._mounted[widget] = dict(
            row=row, col=col,
            row_span=row_span, col_span=col_span,
            sticky=sticky, pad_x=pad_x, pad_y=pad_y,
        )

    def add_all(self, widgets: list[BaseWidget | tuple[BaseWidget, GridLayoutOptions]]):
        for item in widgets:
            if isinstance(item, tuple):
                widget, opts = item
                self._add(widget, **opts)
            else:
                self.add(item)

    def remove(self, widget: BaseWidget):
        if widget in self._mounted:
            widget.widget.grid_forget()
            del self._mounted[widget]

    def configure_row(self, index: int, **options: Unpack[GridRowOptions]):
        self.widget.rowconfigure(index, **options)

    def configure_column(self, index: int, **options: Unpack[GridColumnOptions]):
        self.widget.columnconfigure(index, **options)

    def configure_child(
            self,
            widget: BaseWidget,
            option: str = None,
            **options: Unpack[GridLayoutOptions]
    ):
        if widget not in self._mounted:
            raise ValueError("Widget is not managed by this layout.")
        if option:
            return self._mounted[widget].get(option)
        else:
            self.remove(widget)
            self._add(widget, **options)
            return self

    def _apply_auto_layout(self, options: GridLayoutOptions) -> GridLayoutOptions:
        col_span = options.get("colspan", 1)
        offset = options.pop("offset", 0)
        cols = len(self._columns)

        if self._next_col + offset + col_span > cols:
            self._next_row += 1
            self._next_col = 0

        options.setdefault("row", self._next_row)
        options.setdefault("col", self._next_col + offset)
        self._next_col += offset + col_span

        return options
