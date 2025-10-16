import threading
from tkinter.font import nametofont, Font
from typing import Any, Callable, Concatenate, ParamSpec, TypeVar

from ttkbootstrap.icons import BootstrapIcon
from ttkbootstrap.style.element import Element, ElementImage
from ttkbootstrap.style.style import Style
from ttkbootstrap.style.theme_provider import ThemeProvider
from ttkbootstrap.style.utils import best_foreground, darken_color, lighten_color, mix_colors, relative_luminance

F = TypeVar("F", bound=Callable[..., Any])
P = ParamSpec("P")
R = TypeVar("R")
SelfT = TypeVar("SelfT", bound="StyleManager")

Func = Callable[Concatenate[SelfT, P], R]

_images = []


class OptionManager:
    """Class to manage options"""

    def __init__(self, **kwargs):
        self._options: dict[str, Any] = dict(**kwargs)

    def __call__(self, option=None, **kwargs):
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
        for k, v in kwargs.items():
            self._options.setdefault(k, v)


class StyleManager:
    """Class to manage styles"""
    _variant_registry = {}
    _variant_lock = threading.Lock()

    def create_icon_asset(self, icon: dict, state: str, color: str):
        # create stateful icons to be mapped by the buttons event handling logic
        options = dict(icon)
        options.setdefault('color', color)
        options.setdefault('size', self.icon_font_size())
        self.stateful_icons[state] = BootstrapIcon(**options)

    def build_icon_assets(self):
        icon = self.options("icon")
        if not icon: return
        icon_builder = f"{self.variant}-icon-builder"
        func = self.get(icon_builder)
        func(self, icon)

    def register_stateful_icon(self, icon: dict, state: str, color: str):
        """Substitute and icon image for a specific state if specified and create the icon asset"""
        state_icon = icon.copy()
        state_subs = state_icon.pop('state', {})
        if state in state_subs:
            state_icon['name'] = state_subs[state]
        self.create_icon_asset(state_icon, state, color)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._variant_registry = dict(getattr(cls, "_variant_registry", {}))
        cls._variant_lock = threading.Lock()

    def __init__(self, ttk_class, **options):
        self._ttk_class = ttk_class
        self._style = Style()
        self._provider = ThemeProvider().instance()
        self._options = OptionManager(**options)
        self._options.set_defaults(surface="background")
        self._stateful_icons = dict()

    def icon_font_size(self) -> int:
        """Return the icon size scaled from font size."""
        factor = 0.9 if self.options('icon_only') else 0.72
        fnt = self.get_font(self.options('size'))
        font_size = fnt.metrics('linespace')
        return int(font_size * factor)

    @staticmethod
    def get_font(size: str) -> Font:
        if size == "sm":
            return nametofont("body")
        elif size == "lg":
            return nametofont("body-xl")
        else:
            return nametofont("body-lg")

    @property
    def stateful_icons(self):
        return self._stateful_icons

    @property
    def options(self):
        return self._options

    @property
    def style(self):
        return self._style

    @property
    def theme_name(self):
        return self.provider.name

    @property
    def provider(self):
        return self._provider

    @property
    def colors(self):
        return self.provider.colors

    @property
    def typography(self):
        return self.provider.typography

    @property
    def component_overrides(self):
        return self.provider.components

    @property
    def surface_token(self):
        """The surface color token"""
        return self.options('surface')

    @property
    def color_token(self):
        """The accent color token"""
        return self.options('color')

    @property
    def variant(self):
        """The style variant"""
        return self.options('variant') or 'default'

    @property
    def color_mode(self):
        """The color mode. One of `dark` or `light`"""
        return self.provider.mode

    def resolve_ttk_name(self):
        items = [str(v) for k, v in self.options.items() if k != 'icon']
        # use the icon name and any state names in the generated ttk name
        if 'icon' in self.options.keys():
            items.insert(0, 'IconNormal' + self.options('icon')['name'].title())
            for ik, iv in self.options('icon').get('state', {}).items():
                items.insert(0, 'Icon' + ik.title() + iv.title())
        items.append(self.theme_name)
        items.append(self._ttk_class)
        ttk_style = '.'.join(items).replace('-', '')
        return ttk_style

    def ttk_name_exists(self):
        return self._style.style_exists(self.resolve_ttk_name())

    def build(self):
        name = self.resolve_ttk_name()
        variant = self.options("variant") or "default"
        if name == "tkinter":
            self.resolve_and_build_variant(variant)
        if not self.ttk_name_exists():
            self.resolve_and_build_variant(variant)
        return name

    # ----- Style Aliases ------

    def style_configure(self, style, **kwargs):
        self._style.configure(style, **kwargs)

    def style_map(self, style, **options):
        self._style.map(style, **options)

    def style_create_element(self, element: ElementImage):
        name, args, kwargs = element.build()
        self._style.create_element(name, "image", *args, **kwargs)

    def style_create_layout(self, ttk_style, element: Element):
        self._style.layout(ttk_style, [element.spec()])

    # ----- Style Registry ------

    @classmethod
    def register_variant(cls, variant, *, replace=False):
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

    def resolve_and_build_variant(self, variant):
        func = self.get(variant)
        func(self)

    # ----- Color Utilities & Transformers -----

    def color(self, token: str, surface: str = None, role="background") -> str:
        """Return a color by name."""
        if '-' in token:
            color, level = token.split('-')
            if len(level) == 1:
                if 'subtle' in token:  # color-subtle
                    return self.subtle(color, surface, role)
                else:
                    # color-1 (elevated color)
                    base = self.colors.get(color)
                    return self.elevate(base, int(level))
            elif len(level) == 2:
                if 'subtle' in token:  # color-subtle-2 (elevated subtle color)
                    base = self.subtle(color, surface, role)
                    return self.elevate(base, int(level[1]))

            if level and len(level) == 1:
                if 'subtle' in token:
                    base = self.subtle(color, surface, role)
                    return self.elevate(base, int(level))
                else:
                    base = self.colors.get(color)
                    return self.elevate(base, int(level))
            elif 'subtle' in token:
                color, _ = token.split('-')
                return self.subtle(color, surface, role)
        return self.colors.get(token)

    def subtle(self, token: str, surface=None, role="background") -> str:
        """Return a subtle instance of this color for background or text."""
        base_color = self.colors.get(token)
        surface_color = surface or self.colors.get('background')

        if role == "text":
            # Less blending to keep text legible, just reduce intensity
            if self.provider.mode == "light":
                return darken_color(base_color, 0.25)
            else:
                return lighten_color(base_color, 0.25)
        else:  # background
            if self.provider.mode == "light":
                return mix_colors(base_color, surface_color, 0.08)
            else:
                return mix_colors(base_color, surface_color, 0.10)

    def hover(self, color):
        return self._state_color(color, "hover")

    def active(self, color):
        return self._state_color(color, "active")

    def focus(self, color):
        return self._state_color(color, "focus")

    def focus_border(self, color):
        lum = relative_luminance(color)
        if self.provider.mode == "dark":
            return lighten_color(color, 0.1)
        else:
            return darken_color(color, 0.2 if lum > 0.5 else 0.1)

    def focus_ring(self, color, surface=None):
        surface = surface or self.color(color)
        lum = relative_luminance(color)
        if self.provider.mode == "dark":
            if lum < 0.3:
                brightened = lighten_color(color, 0.2)
                mixed = mix_colors(brightened, surface, 0.2)
            else:
                mixed = mix_colors(color, surface, 0.3)
        else:
            if lum > 0.5:
                blended = mix_colors(color, surface, 0.2)
                mixed = darken_color(blended, 0.15)
            else:
                brightened = lighten_color(color, 0.25)
                mixed = mix_colors(brightened, surface, 0.25)
        return mixed

    def border(self, color):
        if self.provider.mode == "dark":
            return lighten_color(color, 0.20)
        else:
            return darken_color(color, 0.20)

    def on_color(self, color):
        background = self.color('background')
        foreground = self.color('foreground')
        return best_foreground(color, [color, background, foreground])

    def disabled(self, role="background"):
        surface = self.color('background')

        if role == "text":
            if self.provider.mode == "light":
                gray = "#6c757d"  # Bootstrap secondary gray
                mix_ratio = 0.35  # Simulate ~65% opacity
            else:
                gray = "#adb5bd"  # Bootstrap muted text on dark
                mix_ratio = 0.25
        elif role == "background":
            if self.provider.mode == "light":
                gray = "#dee2e6"  # Bootstrap border or card background
                mix_ratio = 0.15
            else:
                gray = "#495057"  # Darker gray surface
                mix_ratio = 0.20
        else:
            raise ValueError(f"Invalid role: {role}. Expected 'text' or 'background'.")

        return mix_colors(gray, surface, mix_ratio)

    def elevate(self, color, elevation=0, max_elevation=5):
        if elevation <= 0:
            return color
        blend_target = "#000000" if self.provider.mode == "light" else "#ffffff"
        weight = min(elevation / max_elevation, 1.0) * 0.3
        return mix_colors(blend_target, color, weight)

    def map_stateful_icons(self):
        s = self.stateful_icons

        # Map ttk states (no 'hover' state; use 'active')
        state_map = [
            ("disabled", s["disabled"]),
            ("selected pressed", s["selected"]),
            ("selected active", s["selected"]),
            ("selected !disabled", s["selected"]),
            ("pressed", s["pressed"]),
            ("active", s["hover"]),
            ("focus", s["focus"]),
            ((), s["normal"]),
        ]

        ttk_style = self.resolve_ttk_name()
        self.style_map(ttk_style, image=state_map)

    @staticmethod
    def _state_color(color, state):
        if state == "focus":
            return color
        delta = {
            "hover": 0.08,
            "active": 0.12,
            "focus": 0.08
        }[state]
        lum = relative_luminance(color)
        if lum < 0.5:
            return lighten_color(color, delta)
        return darken_color(color, delta)
