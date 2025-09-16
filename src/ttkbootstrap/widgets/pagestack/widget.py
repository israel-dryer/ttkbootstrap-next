from __future__ import annotations

from tkinter import ttk
from typing import Any, Optional, Self, Type, Union, Unpack

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.core.layout_context import pop_container, push_container
from ttkbootstrap.events import Event
from ttkbootstrap.exceptions.base import NavigationError
from ttkbootstrap.interop.runtime.binding import Stream
from ttkbootstrap.types import EventHandler, Widget
from ttkbootstrap.utils import assert_valid_keys
from ttkbootstrap.widgets.pagestack.style import PageStackStyleBuilder
from ttkbootstrap.widgets.pagestack.page import GridPage, PackPage
from ttkbootstrap.widgets.pagestack.types import Page, PageOptions, PageStackOptions


class PageStack(BaseWidget):
    """A container for managing and navigating between multiple pages."""

    widget: ttk.Notebook
    Pack: Type[PackPage]
    Grid: Type[GridPage]

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
        self._style_builder = PageStackStyleBuilder()

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
            return self._style_builder.options('variant')
        self._style_builder.options(variant=value)
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
        self.widget.add(widget.tk_name, **widget.page_options)
        self._pages[widget.name] = widget
        return self

    def remove(self, name: str):
        """Remove a page by name."""
        if name in self._pages:
            widget = self._pages.pop(name)
            self.widget.forget(widget.tk_name)
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
        data['page'] = name
        page: Widget = self._pages[name]
        page.emit(Event.PAGE_WILL_MOUNT, data=data)
        self.widget.select(page.tk_name)
        self._current = name
        page.emit(Event.PAGE_MOUNTED, data=data)
        self.emit(Event.PAGE_CHANGED, data=data)
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
            return self.widget.tab(page.tk_name, option)
        elif options is not None:
            self.widget.tab(page.tk_name, **options)
            return self
        return self

    def pages(self):
        """Return a list of all page identifiers."""
        return list(self._pages.keys())

    def on_page_changed(
            self, handler: Optional[EventHandler] = None,
            *, scope="widget") -> Stream[Any] | Self:
        """Stream or chainable binding for <<PageChanged>>

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """
        stream = self.on(Event.PAGE_CHANGED, scope=scope)
        if handler is None:
            return stream
        stream.listen(handler)
        return self

    @staticmethod
    def _validate_options(options: dict):
        """Validate page options for correctness."""
        assert_valid_keys(options, PageOptions, where="pagestack")


PageStack.Pack = PackPage
PageStack.Grid = GridPage
