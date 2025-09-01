from __future__ import annotations
from typing import Any

from ttkbootstrap.types import Widget
from ttkbootstrap.core.layout_context import push_container, pop_container


class ContainerMixin:
    """Expose container-related access on the wrapper, forwarding to the Tk widget.

    - Context manager pushes/pops this wrapper as the current layout container.
    - Property forwarders keep external API consistent with Tk.
    """

    widget: Widget
    parent: Widget

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # --- context manager -------------------------------------------------
    def __enter__(self):
        push_container(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pop_container()

    # --- forwards to underlying Tk widget --------------------------------
    @property
    def master(self) -> Any:
        """Return the Tk master (parent) of the underlying widget."""
        return self.widget.master

    @property
    def tk(self) -> Any:
        """Return the Tcl interpreter associated with the widget."""
        return self.widget.tk

    @property
    def _w(self) -> str:
        """The Tcl window path name (internal)."""
        return self.widget._w

    @property
    def _last_child_ids(self) -> list[str]:
        """Internal list of child IDs (Tk uses this for name generation)."""
        return self.widget._last_child_ids

    @_last_child_ids.setter
    def _last_child_ids(self, value: list[str]):
        self.widget._last_child_ids = value

    @property
    def children(self) -> dict[str, Widget]:
        """Mapping of child widget names to child widgets."""
        return self.widget.children
