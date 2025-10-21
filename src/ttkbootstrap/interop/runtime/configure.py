from __future__ import annotations
from typing import Any, Callable, Dict, Tuple, Optional, Iterable, overload, Literal

from ttkbootstrap.types import Widget
from ttkbootstrap.utils import unsnake, unsnake_kwargs


def configure_delegate(option: str, *, aliases: str | list[str] | None = None):
    """Decorator to mark a method as a configuration delegate.

    This decorator provides a clean, declarative way to register configuration
    options. The decorated method should handle both getting and setting values
    using an optional parameter (following tkinter/ttk conventions).

    Args:
        option: The canonical option name (e.g., "text", "icon").
        aliases: Optional alias(es) for this option.

    Returns:
        The decorated function with metadata attached.

    Examples:
        Basic usage::

            class Button(ConfigureMixin):
                @configure_delegate("text")
                def _configure_text(self, value=None):
                    if value is None:
                        return self._text
                    self._text = value
                    return self

        With aliases::

            class Button(ConfigureMixin):
                @configure_delegate("icon", aliases=["img", "image"])
                def _configure_icon(self, value=None):
                    if value is None:
                        return self._icon
                    self._icon = value
                    return self

        Multiple aliases::

            @configure_delegate("selection", aliases=["sel", "selected"])
            def _configure_selection(self, value=None):
                ...

    Note:
        The decorator only marks the method. Actual registration happens
        automatically via __init_subclass__ when the class is defined.
    """
    def decorator(func):
        func._configure_option = option
        func._configure_aliases = aliases
        return func
    return decorator


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

    def __init_subclass__(cls, **kwargs):
        """Automatically discover and register @configure_delegate decorated methods.

        This method is called when a subclass of ConfigureMixin is defined.
        It scans the class AND its parents (including mixins) for methods decorated
        with @configure_delegate and automatically registers them using add_configure_delegate().
        """
        super().__init_subclass__(**kwargs)

        # Collect decorated methods from this class and all parents
        # We need to check the entire MRO to pick up inherited decorated methods
        # INCLUDING from mixins that don't inherit ConfigureMixin
        decorated_methods = []
        seen_options = set()

        # Walk the MRO to find all decorated methods
        # Start from the most derived class (cls) to allow overriding
        for klass in cls.__mro__:
            # Skip ConfigureMixin itself and object
            if klass is ConfigureMixin or klass is object:
                continue

            for name, attr in list(klass.__dict__.items()):
                if hasattr(attr, '_configure_option'):
                    option = attr._configure_option

                    # Skip if we've already seen this option (child class takes precedence)
                    if option in seen_options:
                        continue

                    seen_options.add(option)
                    aliases = getattr(attr, '_configure_aliases', None)
                    decorated_methods.append((option, name, aliases))

        # Now register them
        for option, name, aliases in decorated_methods:
            # Register using the method name for both getter and setter
            # (following tkinter convention of single method with optional param)
            cls.add_configure_delegate(option, name, name, aliases=aliases)

    # -------------------------
    # Class methods for extending configuration
    # -------------------------
    @classmethod
    def add_configure_delegate(
        cls,
        option: str,
        getter: str | None = None,
        setter: str | None = None,
        *,
        aliases: str | list[str] | None = None
    ):
        """Add a configuration delegate for this class.

        This method allows you to register custom getter/setter methods for configuration
        options, extending the configure() API. It's particularly useful when inheriting
        from classes that use ConfigureMixin.

        Args:
            option: The canonical option name (e.g., "items", "selection").
            getter: Name of the method to call when getting this option's value,
                or None for write-only options.
            setter: Name of the method to call when setting this option's value,
                or None for read-only options.
            aliases: Optional alias(es) for this option. Can be a string or list of strings.

        Returns:
            The class (for method chaining).

        Raises:
            ValueError: If neither getter nor setter is provided.

        Examples:
            Separate getter and setter methods::

                class MyList(ConfigureMixin):
                    def _get_items(self):
                        return self._items

                    def _set_items(self, value):
                        self._items = list(value)

                MyList.add_configure_delegate("items", "_get_items", "_set_items", aliases="data")

            Single accessor method (handles both get and set)::

                class MyWidget(ConfigureMixin):
                    def _selection_accessor(self, value=None):
                        if value is None:
                            return self._selection
                        self._selection = value

                MyWidget.add_configure_delegate("selection", "_selection_accessor", "_selection_accessor")

            Write-only option::

                MyButton.add_configure_delegate("command", setter="_set_command")

            Multiple aliases::

                MyList.add_configure_delegate("items", "_get_items", "_set_items", aliases=["data", "records"])

            Usage after registration::

                widget = MyList()
                widget.configure(items=[1, 2, 3])   # Uses _get_items/_set_items
                widget.configure(data=[4, 5, 6])    # Alias for "items"
                value = widget.configure("items")   # Returns current value
        """
        if not getter and not setter:
            raise ValueError(f"Must provide at least getter or setter for option '{option}'")

        # Ensure class has its own _configure_methods dict (don't mutate parent's)
        if '_configure_methods' not in cls.__dict__:
            # Create a copy of parent's dict
            cls._configure_methods = dict(getattr(cls, '_configure_methods', {}))

        # Add the method mapping
        if getter and setter:
            cls._configure_methods[option] = (getter, setter)
        elif getter:
            cls._configure_methods[option] = (getter, None)
        else:  # setter only
            cls._configure_methods[option] = (None, setter)

        # Add aliases if provided
        if aliases:
            alias_list = [aliases] if isinstance(aliases, str) else aliases
            for alias in alias_list:
                cls.add_configure_alias(alias, option)

        return cls

    @classmethod
    def add_configure_alias(cls, alias: str, target: str):
        """Add an alias for an existing configuration option.

        This allows multiple names to point to the same underlying option,
        providing flexibility in how users configure widgets.

        Args:
            alias: The alias name to add.
            target: The canonical option name that this alias points to.

        Returns:
            The class (for method chaining).

        Examples:
            Single alias::

                MyList.add_configure_alias("data", "items")

            Multiple aliases for same option::

                MyList.add_configure_alias("sel", "selection")
                MyList.add_configure_alias("selected", "selection")

            Method chaining::

                (MyList
                    .add_configure_alias("data", "items")
                    .add_configure_alias("records", "items"))

            Usage::

                widget = MyList()
                widget.configure(items=[1, 2, 3])    # Canonical name
                widget.configure(data=[4, 5, 6])     # Alias
                widget.configure(records=[7, 8, 9])  # Another alias
                # All three set the same underlying option
        """
        # Ensure class has its own _configure_aliases dict (don't mutate parent's)
        if '_configure_aliases' not in cls.__dict__:
            # Create a copy of parent's dict
            cls._configure_aliases = dict(getattr(cls, '_configure_aliases', {}))

        cls._configure_aliases[alias] = target
        return cls


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
