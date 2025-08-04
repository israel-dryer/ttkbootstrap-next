from tkinter import ttk
from typing import Unpack

from ttkbootstrap.core.libtypes import NotebookOptions, NotebookTabOptions
from ttkbootstrap.core.mixins.container import ContainerMixin
from ttkbootstrap.core.widget import BaseWidget, current_layout
from ttkbootstrap.style.builders.notebook import NotebookStyleBuilder
from ttkbootstrap.utils import unsnake_kwargs


# TODO Think about the variants and style options to make available for this widget


class Notebook(BaseWidget, ContainerMixin):
    """
    A themed Notebook widget with tabbed navigation.

    Provides a fluent interface for managing tabs, enabling keyboard traversal,
    and controlling tab visibility and state.
    """

    _configure_methods = {"surface", "background"}

    def __init__(self, parent=None, **kwargs: Unpack[NotebookOptions]):
        """
        Initialize a new Notebook widget.

        Args:
            parent: The parent widget.
            **kwargs: Additional ttk.Notebook keyword arguments.
        """
        parent = parent or current_layout()
        self._style_builder = NotebookStyleBuilder()
        self._widget = ttk.Notebook(parent, **unsnake_kwargs(kwargs))
        super().__init__(parent)
        self.update_style()

    def enable_keyboard_traversal(self):
        """Enable keyboard traversal between tabs."""
        self.widget.enable_traversal()
        return self

    def add(self, child: BaseWidget, text: str, **kwargs: Unpack[NotebookTabOptions]):
        """Add a new tab to the notebook."""
        self.widget.add(child, text=text, **kwargs)
        return self

    def insert(self, position, child: BaseWidget, text: str, **kwargs: Unpack[NotebookTabOptions]):
        """Insert a new tab at the given position."""
        self.widget.insert(position, child, text=text, **kwargs)
        return

    def remove(self, tab: BaseWidget | str):
        """Remove the tab from the notebook."""
        self.widget.forget(str(tab))
        return self

    def hide(self, tab: BaseWidget | str):
        """Hide the tab in the notebook."""
        self.widget.hide(str(tab))
        return self

    def disable(self, tab: BaseWidget | str):
        """Disable the specified tab."""
        self.configure_tab(tab, state="disabled")

    def enable(self, tab: BaseWidget | str):
        """Enable the specified tab."""
        self.configure_tab(tab, state="normal")

    def configure_tab(self, tab: BaseWidget | str, option: str = None, **options: Unpack[NotebookTabOptions]):
        """Get or set the options for a tab."""
        if option is not None:
            return self.widget.tab(str(tab), option)
        else:
            self.widget.option(str(tab), **options)
            return self

    def select_tab(self, tab):
        """Select the specified tab."""
        self.widget.select(str(tab))
        return self

    def select_tab_index(self, index: int):
        """Select tab by index."""
        tab_id = self.widget.tabs()[index]
        self.widget.select(tab_id)

    def get_selected_tab(self):
        """Return the selected tab."""
        return self.widget.select()

    def index_of(self, tab: BaseWidget | str):
        """Return the index of the specified tab."""
        return self.widget.index(str(tab))

    def tab_count(self):
        """Return the number of tabs in the notebook."""
        return int(self.widget.index("end"))

    def get_tabs(self):
        """Return a list of tabs managed by the notebook."""
        return self.widget.tabs()

    def identify_at(self, x: int, y: int):
        """Return the name of the tab element at the given position."""
        return self.widget.identify(x, y)

    def is_tab_visible(self, tab: BaseWidget | str):
        """Return True if the tab is currently visible."""
        return "hidden" not in self.widget.tab(str(tab), "state")
