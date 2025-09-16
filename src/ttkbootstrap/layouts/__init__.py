# ttkbootstrap/layouts/__init__.py
from __future__ import annotations

from importlib import import_module
from typing import Any, TYPE_CHECKING

__all__ = ["Grid", "Pack", "BaseLayout", "types"]

if TYPE_CHECKING:
    from .grid import Grid
    from .pack import Pack
    from .base_layout import BaseLayout
    from . import types  # module export


def __getattr__(name: str) -> Any:
    if name == "Grid":
        return getattr(import_module(".grid", __name__), "Grid")
    if name == "Pack":
        return getattr(import_module(".pack", __name__), "Pack")
    if name == "BaseLayout":
        return getattr(import_module(".base_layout", __name__), "BaseLayout")
    if name == "types":
        return import_module(".types", __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(__all__)
