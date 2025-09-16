import io
import tkinter as tk
from typing import Callable, Literal, Optional, Self, Tuple, Union, Unpack, overload

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.core.mixins.container import ContainerMixin
from ttkbootstrap.events import Event
from ttkbootstrap.widgets.canvas.style import CanvasStyleBuilder
from ttkbootstrap.types import Image, Widget
from ttkbootstrap.utils import unsnake, unsnake_kwargs
from ttkbootstrap.widgets.canvas.types import (
    CanvasArcOptions, CanvasImageOptions, CanvasItemOptions,
    CanvasLineOptions, CanvasOptions, CanvasOvalOptions,
    CanvasPolygonOptions, CanvasRectangleOptions, CanvasTagOrId,
    CanvasTextIndex, CanvasTextOptions, CanvasWidgetOptions
)


class Canvas(BaseWidget, ContainerMixin):
    """A themed canvas widget with drawing, manipulation, and tagging utilities."""

    widget: tk.Canvas
    _configure_methods = {
        "on_yview_change": "on_yview_change",
        "on_xview_change": "on_xview_change"
    }

    def __init__(self, **kwargs: Unpack[CanvasOptions]):
        """
        Initialize a new Canvas widget.

        Args:
            parent: The parent widget.
            **kwargs: Keyword arguments for canvas configuration.
        """
        self._on_xview_change = kwargs.pop("on_xview_change", None)
        self._on_yview_change = kwargs.pop("on_yview_change", None)

        parent = kwargs.pop("parent", None)
        tk_options = dict(
            xscrollcommand=self._on_xview_change,
            yscrollcommand=self._on_yview_change,
            **kwargs
        )

        super().__init__(tk.Canvas, tk_options, parent=parent)

        self._style_builder = CanvasStyleBuilder(self)
        self._style_builder.register_style()
        self._theme = self._style_builder.theme

    def on_yview_change(self, func: Callable = None):
        """Get or set the scrollbar.set command"""
        if func is None:
            return self._on_yview_change
        else:
            self._on_yview_change = func
            self.widget.configure(yscrollcommand=func)
            return self

    def on_xview_change(self, func: Callable = None):
        """Get or set the scrollbar.set command"""
        if func is None:
            return self._on_xview_change
        else:
            self._on_xview_change = func
            self.widget.configure(xscrollcommand=func)
            return self

    def add_widget(self, x: float, y: float, widget: Widget, **kwargs: Unpack[CanvasWidgetOptions]) -> int:
        """Embed a widget at the given (x, y) coordinates."""
        return self.widget.create_window(x, y, window=widget.tk_name, **unsnake_kwargs(kwargs))

    def draw_arc(self, x1: float, y1: float, x2: float, y2: float, **kwargs: CanvasArcOptions) -> int:
        """Draw an arc within a rectangular bounding box."""
        return self.widget.create_arc(x1, y1, x2, y2, **unsnake_kwargs(kwargs))

    def draw_rectangle(self, x1: float, y1: float, x2: float, y2: float, **kwargs: CanvasRectangleOptions) -> int:
        """Draw a rectangle using two corner points."""
        return self.widget.create_rectangle(x1, y1, x2, y2, **unsnake_kwargs(kwargs))

    def draw_oval(self, x1: float, y1: float, x2: float, y2: float, **kwargs: CanvasOvalOptions) -> int:
        """Draw an oval within a rectangular bounding box."""
        return self.widget.create_oval(x1, y1, x2, y2, **unsnake_kwargs(kwargs))

    def draw_line(self, x0, y0, x1, y1, **kwargs: Unpack[CanvasLineOptions]) -> int:
        """Draw a line or series of connected lines."""
        return self.widget.create_line(x0, y0, x1, y1, **unsnake_kwargs(kwargs))

    def draw_text(self, x: float, y: float, text: str = "", **kwargs: CanvasTextOptions) -> int:
        """Draw text at the specified coordinates."""
        bind_fill_to_theme = False
        if 'fill' not in kwargs:
            bind_fill_to_theme = True
            # use default theme color for fill
            surface = self._theme.color(self._style_builder.surface())
            kwargs['fill'] = self._theme.on_color(surface)
        item = self.widget.create_text(x, y, text=text, **unsnake_kwargs(kwargs))
        if bind_fill_to_theme:
            self.on(Event.THEME_CHANGED).listen(
                lambda _: self.configure_item(
                    item, fill=self._theme.on_color(self._theme.color(self._style_builder.surface()))))
        return item

    def draw_polygon(
            self, x0: float, y0: float, x1: float, y1: float,
            *coordinates: float, **kwargs: Unpack[CanvasPolygonOptions]) -> int:
        """Draw a closed polygon from a list of coordinates."""
        return self.widget.create_polygon(x0, y0, x1, y1, *coordinates, **unsnake_kwargs(kwargs))

    def draw_image(self, x: float, y: float, image: Image, **kwargs: Unpack[CanvasImageOptions]) -> int:
        """Draw an image at the specified coordinates."""
        return self.widget.create_image(x, y, image=image, **unsnake_kwargs(kwargs))

    def to_canvas_x(self, screen_x: float, spacing: Union[float, None] = None) -> float:
        """Convert a screen X-coordinate to a canvas X-coordinate."""
        return self.widget.canvasx(screen_x, spacing)

    def to_canvas_y(self, screen_y: float, spacing: Union[float, None] = None) -> float:
        """Convert a screen Y-coordinate to a canvas Y-coordinate."""
        return self.widget.canvasy(screen_y, spacing)

    def get_coordinates(self, item: CanvasTagOrId) -> list[float]:
        """Get the coordinates of a canvas item."""
        return self.widget.coords(item)

    def get_bounding_box(self, *items: CanvasTagOrId) -> Optional[Tuple[int, int, int, int]]:
        """Return the bounding box for one or more canvas items."""
        return self.widget.bbox(*items)

    def start_drag_scroll(self, x: int, y: int):
        """Mark the starting point for drag-based scrolling."""
        self.widget.scan_mark(x, y)
        return self

    def update_drag_scroll(self, x: int, y: int, gain: int = 10):
        """Update scroll position based on drag movement."""
        self.widget.scan_dragto(x, y, gain)
        return self

    def export_as_postscript(self, file_path: str, **options) -> str:
        """Export canvas content as a PostScript file."""
        return self.widget.postscript(file=file_path, **options)

    def export_as_image(self, file_path: str, formatter: str = "PNG", **options) -> None:
        """Export canvas content as an image file using PIL."""
        ps_data = self.widget.postscript(colormode="color", **options)
        image = Image.open(io.BytesIO(ps_data.encode("utf-8")))
        image.save(file_path, format=formatter)

    def move_item(self, item: CanvasTagOrId, dx: float, dy: float):
        """Move a canvas item by a given offset."""
        self.widget.move(item, dx, dy)
        return self

    def move_item_to(self, item: CanvasTagOrId, x: float = 0, y: float = 0):
        """Move an item to a specific coordinate."""
        coordinates = self.widget.coords(item)
        if len(coordinates) >= 2:
            dx = x - coordinates[0]
            dy = y - coordinates[1]
            self.widget.move(item, dx, dy)
        return self

    def delete_item(self, *items: CanvasTagOrId):
        """Delete one or more canvas items."""
        self.widget.delete(*items)
        return self

    def scale_item(self, item: CanvasTagOrId, ox: float, oy: float, sx: float, sy: float):
        """Scale a canvas item relative to an origin point."""
        self.widget.scale(item, ox, oy, sx, sy)
        return self

    def add_tag_above(self, tag: str, item: str):
        """Add a tag to the item above the given item."""
        self.widget.addtag_above(tag, item)
        return self

    def add_tag_below(self, tag: str, item: str):
        """Add a tag to the item below the given item."""
        self.widget.addtag_below(tag, item)
        return self

    def add_tag_closest(self, tag: str, x: float, y: float, halo: float = 0, start: str = None):
        """Add a tag to the item closest to the specified point."""
        self.widget.addtag_closest(tag, x, y, halo, start)
        return self

    def add_tag_enclosed(self, tag: str, x1: float, y1: float, x2: float, y2: float):
        """Add a tag to items enclosed in the specified box."""
        self.widget.addtag_enclosed(tag, x1, y1, x2, y2)
        return self

    def add_tag_with_tag(self, tag: str, existing_tag: str):
        """Add a tag to items with an existing tag."""
        self.widget.addtag_withtag(tag, existing_tag)
        return self

    def add_tag_overlapping(self, tag, x1, y1, x2, y2):
        """Add a tag to items overlapping a bounding box."""
        self.widget.addtag_overlapping(tag, x1, y1, x2, y2)
        return self

    def remove_tag(self, item: CanvasTagOrId, tag: str):
        """Remove a tag from one or more items."""
        # TODO what?
        self.widget.dtag(item, tag)
        return self

    def get_tags(self, item: CanvasTagOrId):
        """Get the list of tags assigned to an item."""
        return self.widget.gettags(item)

    def bind_tag(self, tag: str, sequence=None, func=None, add=None):
        """Bind an event handler to a tag."""
        return self.widget.tag_bind(tag, sequence, func, add)

    def unbind_tag(self, tag, sequence, func_id=None):
        """Unbind an event handler from a tag."""
        self.widget.tag_unbind(tag, sequence, func_id)
        return self

    def raise_item(self, item: CanvasTagOrId, above: CanvasTagOrId = None):
        """Raise an item above another item."""
        self.widget.tag_raise(item, above)
        return self

    def lower_item(self, item: CanvasTagOrId, below: CanvasTagOrId = None):
        """Lower an item below another item."""
        self.widget.tag_lower(item, below)
        return self

    def select_from_index(self, item: CanvasTagOrId, index: CanvasTextIndex):
        """Start selection at the given text index."""
        self.widget.select_from(item, index)
        return self

    def select_to_index(self, item: CanvasTagOrId, index: CanvasTextIndex):
        """Extend selection to the given text index."""
        self.widget.select_to(item, index)
        return self

    def adjust_selection_to_index(self, item: CanvasTagOrId, index: CanvasTextIndex):
        """Adjust selection to include the given index."""
        self.widget.select_adjust(item, index)
        return self

    def clear_selection(self):
        """Clear the current text selection."""
        self.widget.select_clear()
        return self

    def get_selected_item_id(self) -> str | None:
        """Return the item ID currently selected, if any."""
        return self.widget.select_item()

    def insert_text(self, item: CanvasTagOrId, index: CanvasTextIndex, text: str):
        """Insert text into a canvas text item."""
        return self.widget.insert(item, index, text)

    def delete_chars(self, item: CanvasTagOrId, first: CanvasTextIndex, last: CanvasTextIndex):
        """Delete characters between two indices."""
        self.widget.dchars(item, first, last)
        return self

    def set_cursor_index(self, item: CanvasTagOrId, position: CanvasTextIndex):
        """Set the cursor index in a text item."""
        self.widget.icursor(item, position)
        return self

    def get_index(self, item: CanvasTagOrId, position: CanvasTextIndex):
        """Get the resolved index in a text item."""
        return self.widget.index(item, position)

    def configure_item(self, item: CanvasTagOrId, option: str = None, **options: Unpack[CanvasItemOptions]):
        """Configure item options or get a specific option value."""
        if option is not None:
            return self.widget.itemcget(item, unsnake(option))
        else:
            self.widget.itemconfigure(item, **unsnake_kwargs(options))
            return self

    def get_item_type(self, item: CanvasTagOrId):
        """Get the type of the canvas item."""
        return self.widget.type(item)

    def find_items_above(self, item: CanvasTagOrId) -> tuple[int, ...]:
        """Find all items above a specified item."""
        return tuple(self.widget.find_above(item))

    def find_all_items(self) -> tuple[int, ...]:
        """Return all canvas items from bottom to top."""
        return tuple(self.widget.find_all())

    def find_items_below(self, item: CanvasTagOrId) -> tuple[int, ...]:
        """Find all items below a specified item."""
        return tuple(self.widget.find_below(item))

    def find_closest_item(
            self, x: float, y: float, halo: float | None = None,
            start: CanvasTagOrId | None = None) -> tuple[int, ...]:
        """Find the item closest to a given point."""
        args: tuple = (x, y)
        if halo is not None:
            args += (halo,)
        if start is not None:
            args += (start,)
        result = self.widget.find_closest(*args)
        return tuple(result) if isinstance(result, (list, tuple)) else (int(result),)

    def find_items_enclosed(self, x1: float, y1: float, x2: float, y2: float) -> tuple[int, ...]:
        """Find all items completely inside a rectangle."""
        return tuple(self.widget.find_enclosed(x1, y1, x2, y2))

    def find_items_overlapping(self, x1: float, y1: float, x2: float, y2: float) -> tuple[int, ...]:
        """Find all items overlapping a rectangle."""
        return tuple(self.widget.find_overlapping(x1, y1, x2, y2))

    def find_items_with_tag(self, tag: CanvasTagOrId) -> tuple[int, ...]:
        """Find all items associated with a given tag or ID."""
        return tuple(self.widget.find_withtag(tag))

    def focus_item(self, item: CanvasTagOrId | None = None) -> int | None:
        """Set or get the focused canvas item."""
        result = self.widget.focus(item) if item else self.widget.focus()
        return int(result) if result and result.isdigit() else None

    @overload
    def yview(self, how: Literal['moveto'], fraction: float) -> None:
        """Scroll vertically to a fraction [0.0..1.0]"""
        ...

    @overload
    def yview(self, how: Literal['scroll'], number: float, what: Literal["units", "pages"]) -> None:
        """Scroll vertically by a number of units or pages"""
        ...

    @overload
    def yview(self) -> tuple[float, float]:
        """Return a tuple that describes the vertical span of the yview"""
        ...

    def yview(self, *args) -> tuple[float, float] | None:
        """Query or change the vertical position of the view."""
        return self.widget.yview(*args)

    @overload
    def xview(self, how: Literal['moveto'], fraction: float) -> None:
        """Scroll horizontally to a fraction [0.0..1.0]"""
        ...

    @overload
    def xview(self, how: Literal['scroll'], number: float, what: Literal["units", "pages"]) -> None:
        """Scroll horizontally by a number of units or pages"""
        ...

    @overload
    def xview(self) -> tuple[float, float]:
        """Return a tuple that describes the horizontal span of the xview"""
        ...

    def xview(self, *args) -> tuple[float, float] | None:
        """Query or change the horizontal position of the view."""
        return self.widget.xview(*args)

    def scroll_x_to(self, fraction: float) -> Self:
        """Scroll horizontally to a fraction [0.0..1.0]"""
        self.widget.xview_moveto(fraction)
        return self

    def scroll_y_to(self, fraction: float) -> Self:
        """Scroll vertically to a fraction [0.0..1.0]"""
        self.widget.yview_moveto(fraction)
        return self

    def scroll_x_by(self, amount: int, unit: Literal["units", "pages"]) -> Self:
        """Scroll horizontally by a number of units or pages"""
        self.widget.xview_scroll(amount, unit)
        return self

    def scroll_y_by(self, amount: int, unit: Literal["pages", "pages"]) -> Self:
        """Scroll vertically by a number of units or pages"""
        self.widget.yview_scroll(amount, unit)
        return self
