from tkinter import TclError, ttk
from typing import Any, Callable, Literal, Optional, Self, TypedDict, Union, Unpack, cast

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.core.layout_context import pop_container, push_container
from ttkbootstrap.events import Event
from ttkbootstrap.exceptions.base import NavigationError
from ttkbootstrap.interop.runtime.binding import Stream
from ttkbootstrap.layouts import Grid, Pack
from ttkbootstrap.style.builders.notebook import NotebookStyleBuilder
from ttkbootstrap.types import (
    Anchor,
    Compound,
    CoreOptions,
    EventHandler, Fill,
    Gap,
    Image,
    Padding,
    Sticky,
    Widget,
)


class NotebookOptions(CoreOptions, total=False):
    """Options supported by the Notebook widget."""
    take_focus: bool
    width: int
    height: int
    padding: Padding


class NotebookTabOptions(TypedDict, total=False):
    """Common options for configuring Notebook tabs."""
    text: str
    compound: Compound
    image: Image
    underline: int
    state: Literal['normal', 'disabled', 'hidden']


class GridTabOptions(NotebookTabOptions, total=False):
    """Notebook tab options when the tab content is a Grid layout."""
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
    """Notebook tab options when the tab content is a Pack layout."""
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


class TabMixin:
    """Mixin that adds tab metadata and tab-specific options."""
    bind: Callable
    widget: Widget

    def __init__(self, **kwargs):
        """
        Initialize tab mixin.

        Extracts tab-related options (text, image, compound, state, etc.)
        from kwargs and stores them in ``_tab_options`` for later use.
        """
        self._name = kwargs.pop('name', None)
        self._tab_options = dict()
        for key in ['underline', 'state', 'sticky', 'image', 'compound', 'text']:
            if key in kwargs:
                self._tab_options[key] = kwargs.pop(key)

        super().__init__(**kwargs)

    @property
    def name(self):
        """Return the name of this tab."""
        return self._name


class TabGrid(TabMixin, Grid):
    """A Notebook tab whose content uses a Grid layout."""

    def __init__(self, text="", *, name: str = None, **kwargs: Unpack[GridTabOptions]):
        super().__init__(text=text, name=name, **kwargs)
        self._on_activated = None
        self._on_deactivated = None


class TabPack(TabMixin, Pack):
    """A Notebook tab whose content uses a Pack layout."""

    def __init__(self, text="", *, name: str = None, **kwargs: Unpack[PackTabOptions]):
        super().__init__(text=text, name=name, **kwargs)


Tab = Union[str, int, TabGrid, TabPack]


class Notebook(BaseWidget):
    """
    A wrapper around :class:`ttk.Notebook` with simplified tab management
    and name-based lookup support.
    """

    Pack = TabPack
    Grid = TabGrid
    widget: ttk.Notebook

    def __init__(self, **kwargs: Unpack[NotebookOptions]):
        """
        Initialize a Notebook widget.

        **kwargs : NotebookOptions
            Standard notebook options such as ``take_focus``, ``width``,
            ``height``, and ``padding``. Also accepts ``parent`` to specify
            the parent widget.

        Notes
        -----
        This constructor builds the ttk.Notebook with an associated
        style builder and registers it as a managed widget within
        ttkbootstrap.
        """

        self._in_context: bool = False
        self._name_registry: dict[str, Widget] = {}  # map name to ttk tab id
        self._style_builder = NotebookStyleBuilder()

        parent = kwargs.pop('parent', None)
        tk_options = dict(**kwargs)
        super().__init__(ttk.Notebook, tk_options, parent=parent)

    def __enter__(self):
        """Enter layout context; attach self and push as current container."""
        push_container(self)
        self._in_context: bool = True
        return self

    def __exit__(self, exc_type, exc, tb):
        """Exit layout context; pop this container."""
        pop_container()
        self._in_context: bool = False

    def on_tab_changed(
            self, handler: Optional[EventHandler] = None,
            *, scope="widget") -> Stream[Any] | Self:
        """Stream or chainable binding for <<NotebookTabChanged>>

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """
        stream = self.on(Event.NOTEBOOK_TAB_CHANGED, scope=scope)
        if handler is None:
            return stream
        stream.listen(handler)
        return self

    def add(self, widget: Widget, *, name: str = None, **options: Unpack[NotebookTabOptions]):
        """Add a new tab containing the given widget."""
        if hasattr(widget, '_tab_options'):
            opts = getattr(widget, '_tab_options') or dict()
            if opts:
                self.widget.add(widget.tk_name, **opts)
            else:
                self.widget.add(widget.tk_name, **options)

        if name is not None:
            self._name_registry[name] = widget
        if hasattr(widget, 'name'):
            self._name_registry[cast(str, widget.name)] = widget
        return self

    def remove(self, tab: Tab):
        """Remove a tab by widget, index, or registered name."""
        if tab in self._name_registry:
            widget = self._name_registry.pop(tab)
            self.widget.forget(widget.tk_name)
        else:
            self.widget.forget(resolve_name(tab))
        return self

    def hide(self, tab: Tab):
        """Hide a tab temporarily without removing it."""
        if tab in self._name_registry:
            widget = self._name_registry.get(tab)
            self.widget.hide(widget.tk_name)
        else:
            self.widget.hide(resolve_name(tab))

    def tab_index(self, tab: Tab):
        """Return the numeric index of a given tab."""
        if tab in self._name_registry:
            widget = self._name_registry.get(tab)
            self.widget.index(widget.tk_name)
        else:
            self.widget.index(resolve_name(tab))

    def tab_count(self):
        """Return the total number of tabs."""
        return self.widget.index('end')

    def select(self, tab: Tab = None):
        """Select a tab or return the currently selected tab id."""
        if tab is not None:
            if tab in self._name_registry:
                widget = self._name_registry.get(tab)
                self.widget.select(widget.tk_name)
            else:
                try:
                    self.widget.select(resolve_name(tab))
                except TclError as _:
                    raise NavigationError(
                        message=f"No such tab: {tab}",
                        hint="Give the tab a `name`, specify a valid index, or pass in a widget reference.") from None

            return self
        else:
            return self.widget.select()

    def insert(self, position: Literal['end'] | int, widget: Widget, **options: Unpack[NotebookTabOptions]):
        """Insert a tab at the specified position."""
        self.widget.insert(position, widget.tk_name, **options)

    def tab_at_coordinate(self, x: int, y: int):
        """Return the tab index at the given (x, y) coordinate."""
        return self.widget.index(f"@{x},{y}")

    def configure_tab(self, tab: Tab, option: str = None, **options: Unpack[NotebookTabOptions]):
        """Get or set tab configuration options."""
        if option is not None:
            return self.widget.tab(resolve_name(tab), option)
        elif options is not None:
            self.widget.tab(resolve_name(tab), **options)
            return self
        else:
            return self

    def tab_list(self):
        """Return a list of all tab identifiers."""
        return self.widget.tabs()

    def enable_keyboard_traversal(self):
        """Enable keyboard navigation between tabs (Ctrl+Tab, etc.)."""
        self.widget.enable_traversal()

    @staticmethod
    def _validate_options(options: dict):
        """Validate layout options for child widgets."""
        pass


def resolve_name(tab: Tab) -> str:
    """Return the tcl/tk name if exists otherwise the tab"""
    try:
        return tab.tk_name
    except AttributeError:
        return tab
