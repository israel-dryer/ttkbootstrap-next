from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ttkbootstrap.routing.router import Router

_global_router: Router | None = None


def set_router(router: "Router"):
    global _global_router
    _global_router = router


def get_router() -> "Router":
    global _global_router
    from ttkbootstrap.routing.router import Router
    if _global_router is None:
        _global_router = Router([])
    return _global_router


def navigate(path: str, *, replace: bool = False):
    get_router().navigate(path, replace=replace)


def current_path() -> str:
    return get_router().path
