from __future__ import annotations
from ttkbootstrap.layouts.pack import Pack


class View(Pack):
    """Base class for routed views. Subclass this for page containers."""
    # Optional hooks: on_mount(params), on_params(params), on_unmount()


def view(factory):
    factory.__routed_view__ = True
    return factory
