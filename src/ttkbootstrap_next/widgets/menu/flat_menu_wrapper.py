"""Flat menu wrapper that uses custom Toplevel windows for completely flat appearance."""

from typing import Optional, Callable
from .flat_menu import FlatMenu as FlatMenuImpl


class FlatMenu:
    """Menu wrapper that uses custom Toplevel windows instead of native tk.Menu.

    This provides a completely flat menu appearance with no 3D borders,
    unlike native menus which always have borders on Windows.

    API is compatible with the standard Menu class.
    """

    def __init__(self, parent=None, tearoff=False, **kwargs):
        """Initialize flat menu.

        Parameters
        ----------
        parent : widget, optional
            Parent widget
        tearoff : bool
            Ignored (kept for API compatibility)
        **kwargs
            Additional options (mostly ignored for flat menus)
        """
        self.widget = FlatMenuImpl(parent=parent, tearoff=tearoff, **kwargs)
        self._parent = parent

    def add_command(self, label: str = "", command: Optional[Callable] = None, **options):
        """Add a command item to the menu."""
        self.widget.add_command(label=label, command=command, **options)
        return self

    def add_separator(self, **options):
        """Add a separator to the menu."""
        self.widget.add_separator(**options)
        return self

    def add_cascade(self, label: str = "", menu: 'FlatMenu' = None, **options):
        """Add a cascade (submenu) to the menu."""
        submenu = menu.widget if menu else None
        self.widget.add_cascade(label=label, menu=submenu, **options)
        return self

    def add_checkbutton(self, label: str = "", variable=None, onvalue=True, offvalue=False, command: Optional[Callable] = None, **options):
        """Add a checkbutton item to the menu."""
        self.widget.add_checkbutton(label=label, variable=variable, onvalue=onvalue, offvalue=offvalue, command=command, **options)
        return self

    def add_radiobutton(self, label: str = "", variable=None, value=None, command: Optional[Callable] = None, **options):
        """Add a radiobutton item to the menu."""
        self.widget.add_radiobutton(label=label, variable=variable, value=value, command=command, **options)
        return self

    def post(self, x: int, y: int):
        """Show the menu at the specified position."""
        self.widget.post(x, y)
        return self

    def unpost(self):
        """Hide the menu."""
        self.widget.unpost()
        return self

    def delete(self, index1, index2=None):
        """Delete menu items (not yet implemented)."""
        # TODO: Implement delete
        pass

    # Aliases
    show = post
    hide = unpost

    # (Active state helpers removed)
