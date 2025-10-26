import json
import importlib.resources as resources
from typing import Optional, Union, Literal

from ttkbootstrap_next.style.utils import (
    darken_color, tint_color, shade_color, relative_luminance, best_foreground,
    lighten_color, mix_colors
)
from ttkbootstrap_next.exceptions import InvalidThemeError

_registered_themes: dict[str, dict] = {}

_current_theme: Optional["ColorTheme"] = None

default_semantic_tokens = {
    "primary": "blue",
    "secondary": "gray-700",
    "success": "green",
    "info": "cyan",
    "warning": "yellow",
    "danger": "red",
    "light": "gray-100",
    "dark": "gray-900",
    "border": "gray-300"
}


def register_user_theme(name: str, path: str):
    """Register a custom theme with a user-defined name.

    Args:
        name: The name to associate with the theme.
        path: The path to the user theme JSON file.
    """
    data = load_user_defined_theme(path)
    _registered_themes[name] = data


def get_theme(name: str):
    if name in _registered_themes:
        return _registered_themes[name]
    else:
        raise InvalidThemeError("Theme not registered or invalid", name)


def load_default_themes():
    for theme in ["dark.json", "light.json"]:
        data = load_package_theme(theme)
        name: Optional[str] = data.get('name', None)
        if name is not None:
            _registered_themes[name] = data


def load_package_theme(filename: str, package: str = "ttkbootstrap_next.assets.themes") -> dict:
    """Load a JSON file from the given package.

    Args:
        filename: The name of the JSON file.
        package: The package containing the file.

    Returns:
        A dictionary of the parsed JSON data.
    """
    with resources.files(package).joinpath(filename).open("r", encoding="utf-8") as f:
        return json.load(f)


def load_user_defined_theme(path: str) -> dict:
    """Load a JSON theme from a file path outside the package.

    Args:
        path: The absolute or relative path to the JSON theme file.

    Returns:
        A dictionary of the parsed theme JSON.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class ColorTheme:
    """
    Encapsulates theme tokens and provides utilities for derived color states.

    Use ColorTheme.instance() to get the global singleton instance.
    """
    TINT_WEIGHTS = (0.80, 0.60, 0.40, 0.25)
    SHADE_WEIGHTS = (0.25, 0.4, 0.6, 0.85)

    def __init__(self, name: Union[Literal['light', 'dark'], str] = "light"):
        """Initialize the theme from a token dictionary"""
        self._theme = {}
        self._name = "light"
        self._mode = "light"
        self._tokens = {}
        self._colors: dict[str, str] = {}
        self._semantic_tokens = {}
        self.update_semantic_tokens(**default_semantic_tokens)

    def update_semantic_tokens(self, **tokens):
        """Update semantic token mappings."""
        self._semantic_tokens.update(**tokens)

    @staticmethod
    def instance(name: Union[Literal['light', 'dark'], str] = "light"):
        """Return the global ColorTheme singleton.

        Args:
            name: Optional theme name to load if not already initialized.

        Returns:
            ColorTheme: A singleton ColorTheme instance.
        """
        global _current_theme
        if _current_theme is None:
            _current_theme = ColorTheme(name)
        return _current_theme

    @property
    def name(self):
        """Return the current theme name."""
        return self._theme.get('name', 'Unknown')

    @property
    def mode(self):
        """Return 'light' or 'dark' mode."""
        return self._theme.get('mode', 'light')

    def use(self, name: str):
        """Activate a new theme by name."""
        self._theme = get_theme(name)
        self._name = self._theme.get("name", "Unknown")
        self._mode = self._theme.get("mode", "light")
        self._semantic_tokens = self._theme.get("semantic", default_semantic_tokens)
        self._generate_theme_colors()
        self.update_theme_styles()

    def _generate_theme_colors(self):
        """Generate color objects and spectrum variants."""
        # default colors
        self._colors['foreground'] = self._theme.get('foreground', '#000')
        self._colors['background'] = self._theme.get('background', '#fff')
        self._colors['white'] = self._theme.get('white', '#000')
        self._colors['black'] = self._theme.get('black', '#fff')

        # shaded colors
        for color, value in self._theme.get('shades', {}).items():
            self._colors[color] = value
            for _color, _value in self._spectrum(color, value).items():
                self._colors[_color] = _value

        # semantic colors
        for token, value in self._semantic_tokens.items():
            self._colors[token] = self._colors[value]

    def color(self, token: str, surface: str = None, role="background") -> str:
        """Return a Color object by name."""
        if '-' in token:
            color, level = token.split('-')
            if len(level) == 1:
                if 'subtle' in token:  # color-subtle
                    return self.subtle(color, surface, role)
                else:
                    # color-1 (elevated color)
                    base = self._colors.get(color)
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
                    base = self._colors.get(color)
                    return self.elevate(base, int(level))
            elif 'subtle' in token:
                color, _ = token.split('-')
                return self.subtle(color, surface, role)
        return self._colors.get(token)

    def subtle(self, token: str, surface=None, role="background") -> str:
        """Return a subtle instance of this color for background or text."""
        base_color = self._colors.get(token)
        surface_color = surface or self._colors.get('background')

        if role == "text":
            # Less blending to keep text legible, just reduce intensity
            if self._mode == "light":
                return darken_color(base_color, 0.25)
            else:
                return lighten_color(base_color, 0.25)
        else:  # background
            if self._mode == "light":
                return mix_colors(base_color, surface_color, 0.08)
            else:
                return mix_colors(base_color, surface_color, 0.10)

    def hover(self, color: str):
        """Return a hover state color based on the current color."""
        return self._state_color(color, "hover")

    def active(self, color: str):
        """Return an active state color based on the current color."""
        return self._state_color(color, "active")

    def focus(self, color: str):
        """Return a focus state color based on the current color."""
        return self._state_color(color, "focus")

    def focus_border(self, color: str):
        """Return a color suitable for a focus border."""
        lum = relative_luminance(color)
        if self._mode == "dark":
            return lighten_color(color, 0.1)
        else:
            return darken_color(color, 0.2 if lum > 0.5 else 0.1)

    def focus_ring(self, color: str, surface=None) -> str:
        """Return a focus ring color blended with the surface."""
        surface = surface or self.color('color')
        lum = relative_luminance(color)
        if self._mode == "dark":
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

    def border(self, color: str):
        """Return a border color that contrasts against the background."""
        if self._mode == "dark":
            return lighten_color(color, 0.20)
        else:
            return darken_color(color, 0.20)

    def on_color(self, color: str):
        """Return the most readable foreground color on top of this color."""
        background = self.color('background')
        foreground = self.color('foreground')
        return best_foreground(color, [color, background, foreground])

    def disabled(self, role: str = "background") -> str:
        """Return a muted, theme-aware disabled state color"""
        surface = self.color('background')

        if role == "text":
            if self._mode == "light":
                gray = "#6c757d"  # Bootstrap secondary gray
                mix_ratio = 0.35  # Simulate ~65% opacity
            else:
                gray = "#adb5bd"  # Bootstrap muted text on dark
                mix_ratio = 0.25
        elif role == "background":
            if self._mode == "light":
                gray = "#dee2e6"  # Bootstrap border or card background
                mix_ratio = 0.15
            else:
                gray = "#495057"  # Darker gray surface
                mix_ratio = 0.20
        else:
            raise ValueError(f"Invalid role: {role}. Expected 'text' or 'background'.")

        return mix_colors(gray, surface, mix_ratio)

    def elevate(self, color: str, elevation: int = 0, *, max_elevation: int = 5) -> str:
        """Return a raised or layered color to simulate elevation."""
        if elevation <= 0:
            return color
        blend_target = "#000000" if self._mode == "light" else "#ffffff"
        weight = min(elevation / max_elevation, 1.0) * 0.3
        return mix_colors(blend_target, color, weight)

    @classmethod
    def _state_color(cls, color: str, state: Literal["hover", "active", "focus"]) -> str:
        """Return a color variant for a given interaction state."""
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

    @classmethod
    def _spectrum(cls, token, value) -> dict[str, str]:
        """Generate a full color spectrum for a token."""
        spectrum_names = [f'{token}-{x}' for x in [100, 200, 300, 400, 500, 600, 700, 800, 900]]
        tints = [tint_color(value, w) for w in cls.TINT_WEIGHTS]
        shades = [shade_color(value, w) for w in cls.SHADE_WEIGHTS]
        spectrum_colors = [*tints, value, *shades]
        return {name: color for name, color in zip(spectrum_names, spectrum_colors)}

    @staticmethod
    def register_theme_file(name: str, path: str):
        """Register a user-defined theme from a file."""
        register_user_theme(name, path)

    @staticmethod
    def register_theme_definition(name: str, data: dict):
        """Register a user-defined theme from a dictionary."""
        _registered_themes[name] = data

    @staticmethod
    def update_theme_styles():
        """Trigger a style update for the active theme."""
        from tkinter.ttk import Style
        Style().theme_use('clam')

    def __repr__(self):
        """Return a string representation of the current theme."""
        return f"<Theme name={self.name} mode={self.mode}>"


load_default_themes()
