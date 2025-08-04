from typing import Union, Unpack

from tkinter import ttk
from ttkbootstrap.core.libtypes import Orient, PaneOptions, PanedWindowOptions
from ttkbootstrap.core.mixins.container import ContainerMixin
from ttkbootstrap.core.widget import BaseWidget, current_layout
from ttkbootstrap.style.builders.paned_window import PanedWindowStyleBuilder
from ttkbootstrap.style.tokens import ForegroundColor, SurfaceColor
from ttkbootstrap.utils import unsnake, unsnake_kwargs


class PanedWindow(BaseWidget, ContainerMixin):
    """A themed PanedWindow widget using ttk with support for style-based
    configuration and layout behavior.

    Note:
        The `sash_thickness` option modifies the global `Sash` element layout,
        which is shared across all paned window instances and styles. As such,
        updating this value will affect all paned windows application-wide,
        regardless of style name.
    """

    _configure_methods = {"sash_color", "sash_thickness", "orient", "surface"}

    def __init__(
            self,
            parent=None,
            orient: Orient = "horizontal",
            sash_color: ForegroundColor = None,
            sash_thickness: int = 4,
            surface: SurfaceColor = None,
            **kwargs: Unpack[PanedWindowOptions]
    ):
        """Initialize a new PanedWindow.

        Args:
            parent: The parent widget.
            orient: Orientation of panes: 'horizontal' or 'vertical'.
            sash_color: The color of the sash.
            sash_thickness: The thickness of the sash.
            surface: Background surface color.
            **kwargs: Additional ttk PanedWindow options.
        """
        parent = parent or current_layout()
        self._surface_token = surface
        self._widget = ttk.PanedWindow(parent, orient=orient, **unsnake_kwargs(kwargs))
        super().__init__(parent, surface=surface)
        self._style_builder = PanedWindowStyleBuilder(sash_color, sash_thickness, orient)
        self.update_style()

    def surface(self, value: SurfaceColor = None):
        """Get or set the surface token for this widget."""
        if value is None:
            return self._surface_token
        self._surface_token = value
        self._style_builder.surface(value)
        self.update_style()
        return self

    def sash_color(self, value: ForegroundColor = None):
        """Get or set the sash color."""
        if value is None:
            return self._style_builder.sash_color()
        self._style_builder.sash_color(value)
        self.update_style()
        return self

    def sash_thickness(self, value: int = None):
        """Get or set the sash width."""
        if value is None:
            return self._style_builder.sash_thickness()
        self._style_builder.sash_thickness(value)
        self.update_style()
        return self

    def orient(self, value: Orient = None):
        """Get or set the pane orientation."""
        if value is None:
            return self._style_builder.orient()
        self._style_builder.orient(value)
        self.update_style()
        return self

    def add(self, child: BaseWidget, **options: Unpack[PaneOptions]):
        """Add a widget as a new pane at the end of the paned window.

        Args:
            child: The widget to add.
            **options: Pane-specific options (e.g., min_size, sticky).
        """
        self.widget.add(child, **unsnake_kwargs(options))
        return self

    def insert(self, child: BaseWidget, position: Union[int, str], **options: Unpack[PaneOptions]):
        """Insert a widget as a pane at the specified position.

        Args:
            child: The widget to insert.
            position: Index or 'end' position.
            **options: Pane-specific options.
        """
        self.widget.insert(position, child, **unsnake_kwargs(options))
        return self

    def remove(self, child: BaseWidget):
        """Remove a widget from the paned window.

        Args:
            child: The widget to remove.
        """
        self.widget.forget(child)
        return self

    def configure_pane(self, child: BaseWidget, option: str = None, **options: Unpack[PaneOptions]):
        """Get or set the options for a single pane.

        Args:
            child: The pane widget.
            option: Option name to retrieve, if querying.
            **options: Options to set on the pane.

        Returns:
            Option value if querying; otherwise, self.
        """
        if option:
            return self.widget.pane(child, unsnake(option))
        else:
            self.widget.pane(child, **unsnake_kwargs(options))
            return self

    def get_panes(self) -> list[str]:
        """Get a list of pane widget names.

        Returns:
            A list of widget path names.
        """
        return self.widget.panes()

    def identify_at(self, x: int, y: int):
        """Identify the component at the given coordinates.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            A tuple like ('sash', index) or None.
        """
        return self.widget.identify(x, y)
