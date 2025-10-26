from __future__ import annotations

from typing import Unpack

from ttkbootstrap_next.core.base_widget import BaseWidget
from ttkbootstrap_next.events import Event
from ttkbootstrap_next.interop.runtime.binding import Stream
from ttkbootstrap_next.layouts import Grid, Pack
from ttkbootstrap_next.widgets.pagestack.events import NavigationEvent
from ttkbootstrap_next.widgets.pagestack.types import GridPageOptions, PackPageOptions


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

    def on_page_mounted(self) -> Stream[NavigationEvent]:
        """Convenience alias for page mounted stream"""
        return self.on(Event.PAGE_MOUNTED)

    def on_page_will_mount(self) -> Stream[NavigationEvent]:
        """Convenience alias for page will mount stream"""
        return self.on(Event.PAGE_WILL_MOUNT)

    def on_page_unmounted(self) -> Stream[NavigationEvent]:
        """Convenience alias for page unmounted stream"""
        return self.on(Event.PAGE_UNMOUNTED)

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
