from __future__ import annotations

from typing import Any, Callable, Optional, Self, Unpack

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.events import Event
from ttkbootstrap.interop.runtime.binding import Stream
from ttkbootstrap.layouts import Grid, Pack
from ttkbootstrap.types import EventHandler
from ttkbootstrap.widgets.pagestack.events import NavigationEvent
from ttkbootstrap.widgets.pagestack.types import GridPageOptions, PackPageOptions


class PageMixin(BaseWidget):
    """Mixin that provides page lifecycle hooks and metadata."""

    def __init__(self, name: str, **kwargs):
        """
        Initialize the page mixin.

        Args:
            name: The unique name of the page.
            **kwargs: Options forwarded to the base layout widget.
        """
        self._name = name
        self._page_options = {}
        super().__init__(**kwargs)

    def on_page_mounted(
            self, handler: Optional[Callable[[Any], Any]] = None,
            *, scope="widget") -> Stream[NavigationEvent] | Self:
        """Stream or chainable binding for <<PageMounted>>

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """
        stream = self.on(Event.PAGE_MOUNTED, scope=scope)
        if handler is None:
            return stream
        stream.listen(handler)
        return self

    def on_page_will_mount(
            self, handler: Optional[EventHandler] = None,
            *, scope="widget") -> Stream[NavigationEvent] | Self:
        """Stream or chainable binding for <<PageWillMount>>

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """
        stream = self.on(Event.PAGE_WILL_MOUNT, scope=scope)
        if handler is None:
            return stream
        stream.listen(handler)
        return self

    def on_page_unmounted(
            self, handler: Optional[EventHandler] = None,
            *, scope="widget") -> Stream[NavigationEvent] | Self:
        """Stream or chainable binding for <<PageUnmounted>>

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """
        stream = self.on(Event.PAGE_UNMOUNTED, scope=scope)
        if handler is None:
            return stream
        stream.listen(handler)
        return self

    @property
    def name(self):
        """Return the unique name of this page."""
        return self._name

    @property
    def page_options(self):
        """Return additional page options for insertion into a PageStack."""
        return self._page_options


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
