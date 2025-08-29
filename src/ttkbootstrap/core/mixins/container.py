from ttkbootstrap.types import Widget
from ttkbootstrap.core.layout_context import push_container, pop_container


class ContainerMixin:
    """Mixin that exposes container-related access from widget"""

    widget: Widget
    parent: Widget

    def __enter__(self):
        push_container(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pop_container()

    @property
    def master(self):
        return self.widget.master

    @property
    def tk(self):
        return self.widget.tk

    @property
    def _w(self) -> str:
        """The tcl window id"""
        return self.widget._w

    @property
    def _last_child_ids(self) -> list[str]:
        """A list of child ids"""
        return self.widget._last_child_ids

    @_last_child_ids.setter
    def _last_child_ids(self, value: list[str]):
        self.widget._last_child_ids = value

    @property
    def children(self) -> dict[str, Widget]:
        """A list of child widgets"""
        return self.widget.children
