from typing import Any, TypeAlias, TypedDict, Literal, Unpack, Union
from ttkbootstrap.widgets.layout.frame import Frame
from ttkbootstrap.core.widget import BaseWidget, current_layout, layout_context_stack

Sticky = Literal['n', 'e', 's', 'w', 'ns', 'ew', 'nsew', '']


class GridLayoutOptions(TypedDict, total=False):
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


WidgetWithOptions: TypeAlias = tuple[BaseWidget, GridLayoutOptions]


class GridFrame(Frame):

    def __init__(
            self,
            parent=None,
            gap: int | tuple[int, int] = 0,  # (column_gap, row_gap)
            padding: Union[int, tuple[int, int], tuple[int, int, int, int]] = 0,
            cols: int | list[str | int] = 12,
            rows: int | list[str | int] = None,
            auto_layout=True,
            **kwargs
    ):
        parent = parent or current_layout()
        self._gap = self._normalize_gap(gap)
        self._padding = self._normalize_padding(padding)
        self._cols = cols if isinstance(cols, list) else [1] * cols
        self._rows = rows if isinstance(rows, list) else []
        self._auto_layout = auto_layout
        self._next_row = 0
        self._next_col = 0
        self._mounted: dict[BaseWidget, dict] = {}

        # apply padding to self
        super().__init__(parent, padding=self._padding, **kwargs)

        # Column sizing (weight or fixed width)
        for index, col in enumerate(self._cols):
            if isinstance(col, int):
                self.configure_column(index, weight=col)
            elif isinstance(col, str) and col.endswith("px"):
                self.configure_column(index, weight=0)
                self.widget.grid_columnconfigure(index, minsize=int(col.removesuffix("px")))

        # Row sizing (weight or fixed height)
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

    @staticmethod
    def _normalize_gap(gap) -> tuple[int, int]:
        if isinstance(gap, int):
            return gap, gap
        return gap

    @staticmethod
    def _normalize_padding(pad: int | tuple) -> Any:
        if pad is None:
            return 0, 0, 0, 0
        if isinstance(pad, int):
            return pad, pad, pad, pad
        if len(pad) == 2:
            return pad[1], pad[0], pad[1], pad[0]  # top/bottom, left/right
        return pad

    def add(self, widget, **options: Unpack[GridLayoutOptions]):
        if self._auto_layout:
            options = self._apply_auto_layout(options)

        col = options.get("col", 0)
        row = options.get("row", 0)
        col_span = options.get("colspan", 1)
        row_span = options.get("rowspan", 1)
        sticky = options.get("sticky", "ew")

        gap_x = self._gap[0]
        gap_y = self._gap[1]

        # Calculate half-gap padding for all widgets
        left_pad = gap_x // 2
        right_pad = gap_x - left_pad
        top_pad = gap_y // 2
        bottom_pad = gap_y - top_pad

        # Remove padding on layout edges
        if col == 0:
            left_pad = 0
        if (col + col_span) >= len(self._cols):
            right_pad = 0
        if row == 0:
            top_pad = 0
        # Skip bottom-edge check unless row count is known

        pad_x = (left_pad, right_pad)
        pad_y = (top_pad, bottom_pad)

        widget.grid(
            row=row,
            column=col,
            rowspan=row_span,
            columnspan=col_span,
            sticky=sticky,
            padx=pad_x,
            pady=pad_y
        )

        self._mounted[widget] = dict(
            row=row, col=col, row_span=row_span, col_span=col_span,
            sticky=sticky, pad_x=pad_x, pad_y=pad_y
        )

    def add_all(self, widgets: list[BaseWidget | WidgetWithOptions]):
        """Add a sequence of widgets with optional layout configurations."""
        for item in widgets:
            if isinstance(item, tuple):
                widget, opts = item
                self.add(widget, **opts)
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
            self.add(widget, **options)
            return self

    @staticmethod
    def _normalize_pad(pad: int | tuple[int, int]) -> tuple[int, int]:
        if isinstance(pad, int):
            return pad, pad
        return pad

    def _apply_auto_layout(self, options: GridLayoutOptions) -> GridLayoutOptions:
        col_span = options.get("colspan", 1)
        offset = options.pop("offset", 0)
        cols = len(self._cols)

        # apply offset before placement
        if self._next_col + offset + col_span > cols:
            self._next_row += 1
            self._next_col = 0

        options.setdefault("row", self._next_row)
        options.setdefault("col", self._next_col + offset)
        self._next_col += offset + col_span

        return options
