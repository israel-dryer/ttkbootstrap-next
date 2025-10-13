from threading import Lock
from types import MethodType
from typing import Any, Callable, ClassVar, Concatenate, Dict, ParamSpec, TypeVar, cast

from ttkbootstrap.style.element import Element, ElementImage
from ttkbootstrap.style.style import Style
from ttkbootstrap.style.theme import ColorTheme

F = TypeVar("F", bound=Callable[..., Any])
P = ParamSpec("P")
R = TypeVar("R")
SelfT = TypeVar("SelfT", bound="StyleBuilderBase")

Func = Callable[Concatenate[SelfT, P], R]


class OptionManager:
    """A class for managing options"""

    def __init__(self, **kwargs):
        self._options = dict(**kwargs)

    def __call__(self, option: str = None, **kwargs):
        if option:
            return self._options.get(option)
        else:
            self._options.update(**kwargs)
            return self

    def values(self):
        return self._options.values()

    def keys(self):
        return self._options.keys()

    def items(self):
        return self._options.items()

    def set_defaults(self, **kwargs):
        for key, value in kwargs.items():
            self._options.setdefault(key, value)


class StyleBuilderBase:
    _variant_registry: ClassVar[Dict[str, Func]] = {}
    _variant_lock: ClassVar[Lock] = Lock()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._variant_registry = dict(getattr(cls, "_variant_registry", {}))
        cls._variant_lock = Lock()

    def __init__(self, target_style: str, **options):
        self._target = target_style
        self._surface = "background"
        self._theme = ColorTheme.instance()
        self._style = Style()
        self.options = OptionManager(**options)
        self.options.set_defaults(surface="background")

    @property
    def theme(self):
        """The active theme instance"""
        return self._theme

    @property
    def color(self):
        """Convenience alias for `theme.color`"""
        return self._theme.color

    @property
    def on_color(self):
        """Convenience alias for `theme.on_color`"""
        return self._theme.on_color

    def surface(self, value: str = None):
        """Get or set the surface type"""
        if value is None:
            return self.options("surface")
        else:
            self.options(surface=value)
            return self

    def resolve_name(self):
        """Return the resolved ttk style name use to create the style in `ttk.Style`"""
        return ".".join(
            [str(x) for x in self.options.values()] + [self.surface()] + [self.theme.name, self._target]
        )

    def exists(self):
        """Indicates whether or name the existing style name exists in the theme"""
        return self._style.style_exists(self.resolve_name())

    def build(self):
        """Build and return style name"""
        name = self.resolve_name()
        if name == "tkinter":
            self.register_style()
            return name
        elif not self.exists():
            self.register_style()
        return name

    def register_style(self):
        """Register the style (to be implemented by subclass"""
        raise NotImplemented("Must be implemented by subclass")

    def configure(self, style, **kwargs):
        """Configure the style. Convenience alias for `Style.configure`"""
        self._style.configure(style, **kwargs)

    def map(self, style, **options):
        """Configure the state styles. Convenience alias for `Style.map`"""
        self._style.map(style, **options)

    def create_element(self, element: ElementImage):
        """Create a new image element. Convenience alias for `Element.create_element`"""
        name, args, kwargs = element.build()
        self._style.create_element(name, "image", *args, **kwargs)

    def style_layout(self, ttk_style, element: Element):
        """Create a new style layout. Convenience alias for `Style.style_layout`"""
        self._style.layout(ttk_style, [element.spec()])

    @property
    def style(self):
        """The `Style` instance"""
        return self._style

    # ----- Registry ------

    @classmethod
    def register(cls, variant: str, *, replace: bool = False) -> Callable[[F], F]:
        """
        Class-level decorator to register a callable under `variant`.

        Usage:
            @MyBuilder.register("primary")
            def build_primary(self, *args, **kwargs): ...
        """
        if not isinstance(variant, str) or not variant:
            raise ValueError("`variant` must be a non-empty string")

        def deco(func: F) -> F:
            with cls._variant_lock:
                if not replace and variant in cls._variant_registry:
                    raise KeyError(f"Variant '{variant}' already registered")
                cls._variant_registry[variant] = func
            return func

        return deco

    @classmethod
    def get(cls: type[SelfT], variant: str) -> Func[SelfT, P, R]:
        """Return the raw (unbound) callable registered for `variant`."""
        try:
            return cls._variant_registry[variant]  # type: ignore[return-value]
        except KeyError as e:
            raise KeyError(f"Unknown variant '{variant}'. Known: {', '.join(sorted(cls._variant_registry))}") from e

    def resolve(self: SelfT, variant: str) -> Callable[P, R]:
        """
        Return the callable for `variant`, bound to this instance (so the
        registered function can use `self` like a method).
        """
        func = self.get(variant)
        return cast(Callable[P, R], MethodType(func, self))

    def build_with(self, variant: str, *args, **kwargs) -> Any:
        """
        Call the registered variant function bound to this instance.
        Typical use: have the function configure/map/layout and return the style name.
        """
        return self.resolve(variant)(*args, **kwargs)
