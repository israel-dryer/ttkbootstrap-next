from __future__ import annotations

from ttkbootstrap.layouts.layout_context import delegates_layout_context
from importlib import import_module
from typing import Any, TYPE_CHECKING

__all__ = ["Grid", "Pack", "Frame", "delegates_layout_context"]

if TYPE_CHECKING:
    from .grid import Grid
    from .pack import Pack
    from .frame import Frame


def __getattr__(name: str) -> Any:
    if name == "Grid":
        return getattr(import_module(".grid", __name__), "Grid")
    if name == "Pack":
        return getattr(import_module(".pack", __name__), "Pack")
    if name == "Frame":
        return getattr(import_module(".frame", __name__), "Frame")


def __dir__():
    return sorted(__all__)
