from tkinter.ttk import Style as ttkStyle
from typing import Any


class Style:
    """
    A wrapper around tkinter.ttk.Style with a fluent interface.

    Provides simplified access to theme configuration, layout management,
    style lookup, and element creation.
    """

    def __init__(self):
        """
        Initialize a new Style manager using tkinter's ttk.Style.
        """
        self._style = ttkStyle()

    @property
    def ttk(self):
        """Return the underlying ttk.Style instance."""
        return self._style

    def use_theme(self, name: str = None):
        """Get or set the current theme."""
        if name is None:
            return self.ttk.theme_use()
        else:
            self.ttk.theme_use(name)
            return self

    def theme_names(self):
        """Return a list of available theme names."""
        return self.ttk.theme_names()

    def layout(self, style: str, spec: Any = None):
        """Get or set the layout definition for a style."""
        if spec is None:
            return self.ttk.layout(style)
        else:
            self.ttk.layout(style, spec)
            return self

    def configure(self, style: str, lookup: str = None, **options):
        """Get or set style configuration options."""
        if lookup is not None:
            return self.ttk.configure(style, lookup)
        elif options:
            self.ttk.configure(style, **options)
            return self
        else:
            return self.ttk.configure(style)

    def map(self, style: str, lookup: str = None, **options):
        """Get or set dynamic state-based style options."""
        if lookup is not None:
            return self.ttk.map(style, lookup)
        else:
            self.ttk.map(style, **options)
            return self

    def create_element(self, name: str, element_type: str, *args, **kwargs):
        """Create a new element for use in a style layout."""
        self.ttk.element_create(name, element_type, *args, **kwargs)
        return self

    def lookup_element_options(self, name: str):
        """Return the list of configurable options for an element."""
        return self.ttk.element_options(name)

    def lookup_style_option(self, style: str, option: str, state: str = None, fallback_value: str = None):
        """Lookup the value of a style option, optionally by state."""
        return self.ttk.lookup(style, option, state, fallback_value)

    def style_exists(self, style: str):
        """Return True if the style exists (has configuration data)."""

        exists = bool(self.ttk.configure(style))
        return exists
