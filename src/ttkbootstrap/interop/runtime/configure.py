from __future__ import annotations
from typing import Any, Callable, Dict, Tuple, Optional

from ttkbootstrap.types import Widget
from ttkbootstrap.utils import unsnake, unsnake_kwargs


class ConfigureMixin:
    """Unified, alias-aware configuration layer for widgets.

    Subclasses may declare:
      - _configure_methods: Dict[str, str | Tuple[str, str]]
          Maps logical option names to either:
            * a single accessor method name (get when called with no args, set when called with one arg), or
            * a (getter_name, setter_name) tuple of two distinct methods.
      - _configure_aliases: Dict[str, str]
          Maps alias -> canonical logical option (e.g., {"fg": "foreground"}).

    Examples
    --------
    class MyWidget(ConfigureMixin):
        _configure_methods = {
            "surface": "surface",               # one accessor method
            "padding": ("get_padding", "set_padding"),  # separate get/set
        }
        _configure_aliases = {
            "bg": "background",
            "fg": "foreground",
        }
    """

    widget: Widget

    # Optional class-level maps expected from subclasses:
    _configure_methods: Dict[str, str | Tuple[str, str]] = {}
    _configure_aliases: Dict[str, str] = {}

    # Private, per-instance, name-mangled caches
    __cfg_map: Dict[str, Tuple[Optional[Callable[[], Any]], Optional[Callable[[Any], Any]]]]
    __cfg_aliases: Dict[str, str]

    def __init__(self, *args, **kwargs):
        """Cooperative init; prepare handler caches from subclass declarations."""
        self.__cfg_map = {}
        self.__cfg_aliases = dict(getattr(self, "_configure_aliases", {}) or {})
        self.__build_cfg_map()
        super().__init__(*args, **kwargs)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def configure(self, option: str | None = None, /, **kwargs) -> Any:
        """Get or set widget configuration.

        - If `option` is provided (and no kwargs): returns the current value.
        - If kwargs are provided: applies settings and returns `self` (chainable).
        """
        if option is not None and not kwargs:
            return self._get_config(option)
        if kwargs:
            self._set_config(**kwargs)
            return self
        # No option and no kwargs → return all widget options (Tk convention)
        return self.widget.configure()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _set_config(self, **kwargs) -> None:
        """Apply configuration options, dispatching custom handlers first."""
        if not kwargs:
            return

        # Resolve aliases → canonical keys, and split into custom vs passthrough
        passthrough: Dict[str, Any] = {}
        for raw_key, value in list(kwargs.items()):
            key = self.__resolve_alias(raw_key)
            getter, setter = self.__cfg_map.get(key, (None, None))

            if setter is not None:
                # Custom setter consumes this arg
                setter(value)
            else:
                # Defer to ttk widget; keep original raw_key so unsnake_kwargs can format it
                passthrough[raw_key] = value

        if passthrough:
            self.widget.configure(**unsnake_kwargs(passthrough))

    def _get_config(self, option: str) -> Any:
        """Retrieve a single configuration value, via custom getter or widget.cget."""
        key = self.__resolve_alias(option)
        getter, _setter = self.__cfg_map.get(key, (None, None))
        if getter is not None:
            return getter()
        return self.widget.cget(unsnake(option))

    # ------------------------------------------------------------------
    # Build handler map
    # ------------------------------------------------------------------
    def __build_cfg_map(self) -> None:
        """Compile `_configure_methods` into fast getter/setter callables."""
        methods = getattr(self, "_configure_methods", {}) or {}

        for logical_key, spec in methods.items():
            canon = logical_key  # maintain declared key; aliasing handled elsewhere

            if isinstance(spec, tuple):
                get_name, set_name = spec
                getter = getattr(self, get_name) if get_name else None
                setter = getattr(self, set_name) if set_name else None
            else:
                # Single accessor: call with no args to get, with one arg to set
                accessor = getattr(self, spec)
                getter = lambda acc=accessor: acc()  # bind name now
                setter = lambda v, acc=accessor: acc(v)

            # Sanity: ensure callables (allow None for either side in tuple form)
            if getter is not None and not callable(getter):
                raise TypeError(f"Getter for '{logical_key}' is not callable.")
            if setter is not None and not callable(setter):
                raise TypeError(f"Setter for '{logical_key}' is not callable.")

            self.__cfg_map[canon] = (getter, setter)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def __resolve_alias(self, key: str) -> str:
        """Map alias → canonical key if present; otherwise return key unchanged."""
        return self.__cfg_aliases.get(key, key)
