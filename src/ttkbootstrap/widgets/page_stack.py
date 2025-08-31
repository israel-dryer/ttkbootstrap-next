from tkinter import TclError, ttk
from typing import Any, Callable, Literal, Optional, Type, TypedDict, Union, Unpack, cast
from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.core.layout_context import pop_container, push_container
from ttkbootstrap.events import Event
from ttkbootstrap.exceptions.base import NavigationError
from ttkbootstrap.layouts import Pack, Grid
from ttkbootstrap.style.builders.notebook import NotebookStyleBuilder
from ttkbootstrap.types import Anchor, CoreOptions, Fill, Gap, Padding, Sticky, Widget
from ttkbootstrap.utils import assert_valid_keys

Page = Union["GridPage", "PackPage"]


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


class PageStack(BaseWidget):
    """A container for managing and navigating between multiple pages."""

    widget: ttk.Notebook
    Pack: Type["PackPage"]
    Grid: Type["GridPage"]
    _configure_methods = {"surface": "surface"}

    def __init__(self, **kwargs: Unpack[PageStackOptions]):
        """
        Initialize a new PageStack.

        Args:
            **kwargs: Options controlling stack configuration, including
                width, height, padding, and whether the stack can take focus.
        """
        self._pages: dict[str, Widget] = {}
        self._current: Optional[str] = None
        self._history: list[tuple[str, dict]] = []
        self._index: int = -1
        self._style_builder = NotebookStyleBuilder(variant='pages')

        parent = kwargs.pop('parent', None)
        tk_options = dict(**kwargs)
        super().__init__(ttk.Notebook, tk_options, parent=parent)

    def __enter__(self):
        """Enter layout context; push self as the current container."""
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb):
        """Exit layout context; pop self from the container stack."""
        pop_container()

    def variant(self, value: str = None):
        """Get or set the current style variant."""
        if value is None:
            return self._style_builder.variant()
        self._style_builder.variant(value)
        self.update_style()
        return self

    def surface(self, value: str = None):
        """Get or set the current surface style token."""
        if value is None:
            return self._style_builder.surface()
        self._style_builder.surface(value)
        self.update_style()
        return self

    def add(self, widget: Page):
        """Add a new page to the stack."""
        self.widget.add(cast(Widget, widget), **widget.page_options)
        self._pages[widget.name] = widget
        return self

    def remove(self, name: str):
        """Remove a page by name."""
        if name in self._pages:
            widget = self._pages.pop(name)
            self.widget.forget(widget)
        else:
            self.widget.forget(name)
        return self

    def page_count(self):
        """Return the total number of pages in the stack."""
        return len(self._pages)

    def navigate(self, name: str, *, data: Optional[dict] = None, replace: bool = False):
        """Navigate to the page with the given name."""
        if name not in self._pages:
            raise NavigationError(f"{name} is not a valid page.")

        if replace and 0 <= self._index < len(self._history):
            self._history[self._index] = (name, data)
        else:
            if self._index < len(self._history) - 1:
                self._history = self._history[: self._index + 1]
            self._history.append((name, data))
            self._index += 1

        if self._current is not None:
            self._pages[self._current].emit(Event.PAGE_UNMOUNTED)

        data = dict(data or {})
        page: Widget = self._pages[name]
        page.emit(Event.PAGE_WILL_MOUNT, data=data)
        self.widget.select(page)
        self._current = name
        page.emit(Event.PAGE_MOUNTED, data=data)
        return self

    def back(self):
        """Navigate to the previous page in the navigation history."""
        if self._index > 0:
            self._index -= 1
            name, data = self._history[self._index]
            self.navigate(name, data=data, replace=True)
        return self

    def forward(self):
        """Navigate to the next page in the navigation history."""
        if self._index < len(self._history) - 1:
            self._index += 1
            name, data = self._history[self._index]
            self.navigate(name, data=data, replace=True)
        return self

    def current(self) -> tuple[str, dict] | None:
        """Return the current page name and its navigation data."""
        if self._current is None:
            return None
        return self._current, (self._history[self._index][1] if self._index >= 0 else {})

    def configure_page(self, page: Union[Page, str], option: PageOptions = None, **options: Unpack[PageOptions]):
        """Get or set configuration options for a page."""
        if option is not None:
            return self.widget.tab(page, option)
        elif options is not None:
            self.widget.tab(page, **options)
            return self
        return self

    def pages(self):
        """Return a list of all page identifiers."""
        return list(self._pages.keys())

    @staticmethod
    def _validate_options(options: dict):
        """Validate page options for correctness."""
        assert_valid_keys(options, PageOptions, where="pagestack")


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


class PageMixin:
    """Mixin that provides page lifecycle hooks and metadata."""

    bind: Callable
    widget: Widget

    def __init__(self, name: str, **kwargs):
        """
        Initialize the page mixin.

        Args:
            name: The unique name of the page.
            **kwargs: Options forwarded to the base layout widget.
        """
        self._name = name
        self._on_page_mounted = None
        self._on_page_will_mount = None
        self._on_page_unmounted = None
        self._page_options = {}
        super().__init__(**kwargs)
        self._bind_lifecycle_events()

    def _bind_lifecycle_events(self) -> None:
        """Bind internal dispatchers to lifecycle events."""
        if not hasattr(self, "widget") or getattr(self, "widget", None) is None:
            raise RuntimeError("PageMixin expects a BaseWidget with .widget")
        if not callable(getattr(self, "bind", None)):
            raise RuntimeError("PageMixin expects .bind(...) on the concrete class")

        try:
            if self.widget.winfo_exists():
                self.bind(Event.PAGE_MOUNTED, self._dispatch_page_mounted, add=False)
                self.bind(Event.PAGE_WILL_MOUNT, self._dispatch_page_will_mount, add=False)
                self.bind(Event.PAGE_UNMOUNTED, self._dispatch_page_unmounted, add=False)
        except TclError as e:
            msg = str(e).lower()
            if "invalid command name" in msg or "has been destroyed" in msg:
                return
            raise

    def _dispatch_page_mounted(self, event: dict):
        """Internal dispatcher for PAGE_MOUNTED events."""
        if self._on_page_mounted:
            return self._on_page_mounted(event)
        return None

    def _dispatch_page_will_mount(self, event: dict):
        """Internal dispatcher for PAGE_WILL_MOUNT events."""
        if self._on_page_will_mount:
            return self._on_page_will_mount(event)
        return None

    def _dispatch_page_unmounted(self, event: dict):
        """Internal dispatcher for PAGE_UNMOUNTED events."""
        if self._on_page_unmounted:
            return self._on_page_unmounted(event)
        return None

    @property
    def name(self):
        """Return the unique name of this page."""
        return self._name

    @property
    def page_options(self):
        """Return additional page options for insertion into a PageStack."""
        return self._page_options

    def on_page_mounted(self, func: Callable[[dict], Any] = None):
        """Get or set the PAGE_MOUNTED callback."""
        if func is None:
            return self._on_page_mounted
        self._on_page_mounted = func
        return self

    def on_page_unmounted(self, func: Callable[[dict], Any] = None):
        """Get or set the PAGE_UNMOUNTED callback."""
        if func is None:
            return self._on_page_unmounted
        self._on_page_unmounted = func
        return self

    def on_page_will_mount(self, func: Callable[[dict], Any] = None):
        """Get or set the PAGE_WILL_MOUNT callback."""
        if func is None:
            return self._on_page_will_mount
        self._on_page_will_mount = func
        return self


class PackPage(PageMixin, Pack):
    """A page within a PageStack that uses a Pack layout."""

    def __init__(self, name: str, **kwargs: Unpack[PackPageOptions]):
        """
        Initialize a PackPage.

        Args:
            name: The unique page name.
            **kwargs: Layout options forwarded to the Pack container.
        """
        super().__init__(name, **kwargs)


class GridPage(PageMixin, Grid):
    """A page within a PageStack that uses a Grid layout."""

    def __init__(self, name: str, **kwargs: Unpack[GridPageOptions]):
        """
        Initialize a GridPage.

        Args:
            name: The unique page name.
            **kwargs: Layout options forwarded to the Grid container.
        """
        super().__init__(name, **kwargs)


PageStack.Pack = PackPage
PageStack.Grid = GridPage

__all__ = ["PageStack"]
