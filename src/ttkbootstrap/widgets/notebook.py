from typing import Literal, TypedDict, Union, Unpack
from tkinter import ttk
from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.core.layout_context import pop_container, push_container
from ttkbootstrap.style.builders.notebook import NotebookStyleBuilder
from ttkbootstrap.types import Compound, CoreOptions, Padding, Sticky, Widget, Image
from ttkbootstrap.utils import assert_valid_keys

Tab = Union[str, int, Widget]


class NotebookOptions(CoreOptions, total=False):
    take_focus: bool
    width: int
    height: int
    padding: Padding


class NotebookTabOptions(TypedDict, total=False):
    name: str
    state: Literal['normal', 'disabled', 'hidden']
    sticky: Sticky
    padding: Padding
    text: str
    image: Image
    compound: Compound
    underline: int


class Notebook(BaseWidget):
    """
    A wrapper around :class:`ttk.Notebook` with simplified tab management
    and name-based lookup support.
    """

    widget: ttk.Notebook
    _configure_methods = {"surface": "surface", "variant": "variant"}
    _name_registry: dict[str, Widget] = {}  # map name to ttk tab id

    def __init__(self, *, variant=None, surface=None, **kwargs: Unpack[NotebookOptions]):
        """
        Initialize a Notebook widget.

        Parameters
        ----------
        variant : str, optional
            Style variant name applied via the :class:`NotebookStyleBuilder`.
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
        self._style_builder = NotebookStyleBuilder(variant=variant, surface=surface)
        parent = kwargs.pop('parent', None)
        tk_options = dict(**kwargs)
        super().__init__(ttk.Notebook, tk_options, parent=parent)

    def __enter__(self):
        """Enter layout context; attach self and push as current container."""
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb):
        """Pop this container from the context."""
        pop_container()

    def variant(self, value: str = None):
        if value is None:
            return self._style_builder.variant()
        else:
            self._style_builder.variant(value)
            self.update_style()
            return self

    def surface(self, value: str = None):
        if value is None:
            return self._style_builder.surface()
        else:
            self._style_builder.surface(value)
            self.update_style()
            return self

    def add(self, widget: Widget, *, name: str = None, **options: Unpack[NotebookTabOptions]):
        """Add a tab containing the given widget."""
        print("adding", widget)
        self.widget.add(widget, **options)
        if name is not None:
            self._name_registry[name] = widget
        return self

    def remove(self, tab: Tab):
        """Remove a tab by widget, index, or registered name."""
        if tab in self._name_registry:
            widget = self._name_registry.pop(tab)
            self.widget.forget(widget)
        else:
            self.widget.forget(tab)
        return self

    def hide(self, tab: Tab):
        """Temporarily hide a tab without removing it."""
        if tab in self._name_registry:
            widget = self._name_registry.get(tab)
            self.widget.hide(widget)
        else:
            self.widget.hide(tab)

    def tab_index(self, tab: Tab):
        """Return the numeric index of the given tab."""
        if tab in self._name_registry:
            widget = self._name_registry.get(tab)
            self.widget.index(widget)
        else:
            self.widget.index(tab)

    def tab_count(self):
        """Return the total number of tabs."""
        return self.widget.index('end')

    def select(self, tab: Tab = None):
        """Select a tab or return the currently selected tab."""
        if tab is not None:
            if tab in self._name_registry:
                widget = self._name_registry.get(tab)
                self.widget.select(widget)
            else:
                self.widget.select(tab)
            return self
        else:
            return self.widget.select()

    def insert(self, position: Literal['end'] | int, widget: Widget, **options: Unpack[NotebookTabOptions]):
        """Insert a new tab at the given position."""
        self.widget.insert(position, widget, **options)

    def tab_at_coordinate(self, x: int, y: int):
        """Return the tab identifier at a given (x, y) coordinate."""
        return self.widget.identify(x, y)

    def configure_tab(self, tab: Tab, option: NotebookTabOptions = None, **options: Unpack[NotebookTabOptions]):
        """Get or set tab configuration options."""
        if option is not None:
            return self.widget.tab(tab, option)
        elif options is not None:
            self.widget.tab(tab, **options)
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
        """Validate layout options for child widgets"""
        assert_valid_keys(
            options,
            NotebookTabOptions,
            where="notebook"
        )
