from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence, Dict, TYPE_CHECKING, Tuple, Type

from ttkbootstrap.routing.navigation import set_router
from .patterns import compile_pattern, match_path, CompiledPattern


if TYPE_CHECKING:
    from ttkbootstrap.routing.outlet import RouterOutlet
    from ttkbootstrap.layouts.pack import Pack


class NavigationError(Exception):
    def __init__(self, message: str, code: str = "ROUTER_NAV_ERROR"):
        super().__init__(message)
        self.code = code


@dataclass
class Route:
    path: str
    view: Callable[..., "Pack"]
    name: Optional[str] = None
    before_enter: Optional[Callable[[Dict[str, str]], bool]] = None
    children: Sequence["Route"] | None = None
    _compiled: CompiledPattern | None = field(default=None, init=False, repr=False)

    def compile(self):
        if self._compiled is None:
            self._compiled = compile_pattern(self.path)
        return self._compiled


class History:
    def __init__(self):
        self._entries: List[str] = ["/"]
        self._index: int = 0

    @property
    def current(self) -> str:
        return self._entries[self._index]

    def push(self, path: str):
        del self._entries[self._index + 1:]
        self._entries.append(path)
        self._index += 1

    def replace(self, path: str):
        self._entries[self._index] = path

    def can_go(self, delta: int) -> bool:
        j = self._index + delta
        return 0 <= j < len(self._entries)

    def go(self, delta: int) -> str:
        j = self._index + delta
        if 0 <= j < len(self._entries):
            self._index = j
            return self._entries[self._index]
        raise NavigationError("Cannot move in history", code="ROUTER_HISTORY_BOUNDS")


class Router:
    def __init__(self, routes: Sequence[Route] | None = None):
        self.routes: List[Route] = list(routes or [])
        for r in self.routes:
            r.compile()
        self._outlets: List["RouterOutlet"] = []
        self._history = History()
        self._params: Dict[str, str] = {}
        self._current_route: Route | None = None
        set_router(self)

    def register_outlet(self, outlet: "RouterOutlet"):
        if outlet not in self._outlets:
            self._outlets.append(outlet)
            outlet.emit('<<RouterAttached>>')

    def unregister_outlet(self, outlet: "RouterOutlet"):
        if outlet in self._outlets:
            self._outlets.remove(outlet)

    @property
    def path(self) -> str:
        return self._history.current

    @property
    def params(self) -> Dict[str, str]:
        return dict(self._params)

    def navigate(self, path: str, *, replace: bool = False, outlet: str = None):
        match = self._match_route(path)
        if match is None:
            raise NavigationError(f"No route matches '{path}'", code="ROUTER_NO_MATCH")
        route, params = match
        if route.before_enter and not bool(route.before_enter(params)):
            raise NavigationError("before_enter guard blocked navigation", code="ROUTER_GUARDED")
        self._current_route = route
        self._params = params
        if replace:
            self._history.replace(path)
        else:
            self._history.push(path)

        if outlet is None and len(self._outlets) > 0:
            return self._outlets[0]._router_navigated(route, params)
        else:
            _outlet = [x for x in self._outlets if x.outlet_name == outlet]
            if len(_outlet) == 1:
                return _outlet[0]._router_navigated(route, params)
            else:
                raise NavigationError(f"No router found with name {outlet}")

    def replace(self, path: str):
        self.navigate(path, replace=True)

    def go(self, delta: int):
        path = self._history.go(delta)
        match = self._match_route(path)
        if match is None:
            raise NavigationError(f"History path '{path}' no longer matches", code="ROUTER_NO_MATCH")
        route, params = match
        self._current_route = route
        self._params = params
        for outlet in list(self._outlets):
            # I think these can be replaced by outlet.emit()
            outlet._router_navigated(route, params)

    def _match_route(self, path: str) -> Optional[Tuple[Route, Dict[str, str]]]:
        for r in self.routes:
            params = match_path(r.compile(), path)
            if params is not None:
                return (r, params)
        return None
