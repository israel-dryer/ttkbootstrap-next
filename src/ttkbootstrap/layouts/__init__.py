from __future__ import annotations

from ttkbootstrap.layouts.layout_context import delegates_layout_context
from importlib import import_module
from typing import Any, TYPE_CHECKING

__all__ = ["Grid", "Pack", "delegates_layout_context"]

if TYPE_CHECKING:
    from .grid import Grid
    from .pack import Pack


def __getattr__(name: str) -> Any:
    if name == "Grid":
        return getattr(import_module(".grid", __name__), "Grid")
    if name == "Pack":
        return getattr(import_module(".pack", __name__), "Pack")


def __dir__():
    return sorted(__all__)
