from __future__ import annotations
from typing import Any, Callable, Dict, Tuple, Optional, Iterable, overload, Literal

from ttkbootstrap.types import Widget
from ttkbootstrap.utils import unsnake, unsnake_kwargs


class ConfigureMixin:
    widget: Widget

    _configure_methods: Dict[str, str | Tuple[str, str]] = {}
    _configure_aliases: Dict[str, str] = {}
    _configure_strict: bool = False  # <— opt-in: raise on unknown logical options

    __cfg_map: Dict[str, Tuple[Optional[Callable[[], Any]], Optional[Callable[[Any], Any]]]]
    __cfg_aliases: Dict[str, str]

    def __init__(self, *args, **kwargs):
        self.__cfg_map = {}
        self.__cfg_aliases = dict(getattr(self, "_configure_aliases", {}) or {})
        self.__build_cfg_map()
        super().__init__(*args, **kwargs)

    # -------------------------
    # Public API (overloads)
    # -------------------------
    @overload
    def configure(self, option: str, /, **kwargs: Any) -> Any:
        ...

    @overload
    def configure(self, option: Iterable[str], /, **kwargs: Any) -> Dict[str, Any]:
        ...

    @overload
    def configure(self, option: None = None, /, **kwargs: Any) -> Any:
        ...

    def configure(self, option: str | Iterable[str] | None = None, /, **kwargs) -> Any:
        """
        Get or set configuration.

        - configure("text") -> current value
        - configure(["text","state"]) -> {"text": ..., "state": ...}
        - configure(text="Save", padding=4) -> self (chainable)
        - configure() -> widget.configure() (Tk metadata dict)
        """
        if option is not None and kwargs:
            raise ValueError("Pass either a single/multi option to get, or kwargs to set—not both.")

        if option is not None and not kwargs:
            # Multi-get
            if isinstance(option, (list, tuple, set)):
                return {opt: self._get_config(opt) for opt in option}
            # Single-get
            return self._get_config(option)

        if kwargs:
            self._set_config(**kwargs)
            return self

        return self.widget.configure()

    # -------------------------
    # Internals
    # -------------------------
    def _set_config(self, **kwargs) -> None:
        if not kwargs:
            return

        passthrough: Dict[str, Any] = {}
        for raw_key, value in list(kwargs.items()):
            key = self.__resolve_alias(raw_key)
            getter, setter = self.__cfg_map.get(key, (None, None))

            if setter is not None:
                setter(value)
            else:
                if self._configure_strict and key not in self.__cfg_map:
                    # If it's not a known logical key, we still allow passthrough to Tk,
                    # but in strict mode ensure it actually exists on the widget.
                    try:
                        # Peek once to validate existence; cget raises if unknown.
                        self.widget.cget(unsnake(key))
                    except Exception as e:
                        raise KeyError(f"Unknown option '{raw_key}' (canonical '{key}')") from e
                # Keep the original raw key so unsnake_kwargs can format it
                passthrough[raw_key] = value

        if passthrough:
            self.widget.configure(**unsnake_kwargs(passthrough))

    def _get_config(self, option: str) -> Any:
        key = self.__resolve_alias(option)
        getter, _setter = self.__cfg_map.get(key, (None, None))

        if getter is not None:
            return getter()

        # Use canonical key for passthrough cget (fixes alias leakage)
        return self.widget.cget(unsnake(key))

    # -------------------------
    # Build handler map
    # -------------------------
    def __build_cfg_map(self) -> None:
        methods = getattr(self, "_configure_methods", {}) or {}

        for logical_key, spec in methods.items():
            canon = logical_key

            if isinstance(spec, tuple):
                get_name, set_name = spec
                getter = getattr(self, get_name) if get_name else None
                setter = getattr(self, set_name) if set_name else None
            else:
                accessor = getattr(self, spec)
                # Bind now to avoid late-binding surprises
                getter = (lambda acc=accessor: acc())
                setter = (lambda v, acc=accessor: acc(v))

            if getter is not None and not callable(getter):
                raise TypeError(f"Getter for '{logical_key}' is not callable.")
            if setter is not None and not callable(setter):
                raise TypeError(f"Setter for '{logical_key}' is not callable.")

            self.__cfg_map[canon] = (getter, setter)

    # -------------------------
    # Helpers
    # -------------------------
    def __resolve_alias(self, key: str) -> str:
        return self.__cfg_aliases.get(key, key)
