import json
import importlib.resources as resources
from typing import Optional, Union, Literal

from .utils import darken_color, tint_color, shade_color, relative_luminance, best_foreground, lighten_color, \
    should_darken, mix_colors
from ..core.libtypes import ColorTokenType, SurfaceRoleType, ColorShadeType
from ..exceptions import InvalidThemeError

_registered_themes: dict[str, dict] = {}

_current_theme: Optional["ColorTheme"] = None


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


def load_package_theme(filename: str, package: str = "ttkbootstrap.assets.themes") -> dict:
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


TINT_WEIGHTS = (0.10, 0.25, 0.40, 0.55)
SHADE_WEIGHTS = (0.90, 0.75, 0.60, 0.45)

Themes = Union[
    Literal['light', 'dark'],
    str  # user defined themes
]


class ColorTheme:
    """
    Encapsulates theme tokens and provides utilities for derived color states.

    Use ColorTheme.instance() to get the global singleton instance.
    """

    def __init__(self, name: Themes = "light"):
        """Initialize the theme from a token dictionary.

        Args:
            name: The theme name.
        """
        self._name = "light"
        self._mode = "light"
        self._tokens = {}
        self.use(name)

    @property
    def name(self):
        """The theme name"""
        return self._name

    @property
    def mode(self):
        """indicates dark or light mode"""
        return self._mode

    @property
    def tokens(self):
        """A collection of theme color tokens"""
        return self._tokens

    @staticmethod
    def register_theme_file(name: str, path: str):
        """Register a new user defined theme from file source"""
        register_user_theme(name, path)

    @staticmethod
    def instance(name: Themes = "light"):
        """Return the current global ColorTheme instance, initializing if necessary.

        Args:
            name: Optional theme name to load if not already initialized.

        Returns:
            A singleton ColorTheme instance.
        """
        global _current_theme
        if _current_theme is None:
            _current_theme = ColorTheme(name)
        return _current_theme

    @staticmethod
    def register_theme_definition(name: str, data: dict):
        """Register a new user defined theme from data object"""
        _registered_themes[name] = data

    def use(self, name: str):
        theme = get_theme(name)
        self._name = theme.get("name", "Unknown")
        self._mode = theme.get("mode", "light")
        self._tokens = theme.get("colors", {})
        self.update_theme_styles()

    @staticmethod
    def update_theme_styles():
        """Trigger a style update on all widgets"""
        from tkinter.ttk import Style
        Style().theme_use('clam')

    def color(self, token: ColorTokenType) -> str:
        """Get the hex value of a token."""
        return self.tokens.get(token)

    def spectrum(self, token: ColorTokenType) -> dict[int, str]:
        """Get the full color spectrum (tints, base, shades) for a token."""
        base = self.color(token)
        spectrum_names = [100, 200, 300, 400, 500, 600, 700, 800, 900]
        tints = [tint_color(base, w) for w in TINT_WEIGHTS]
        shades = [shade_color(base, w) for w in SHADE_WEIGHTS]
        spectrum_colors = [*tints, base, *shades]
        return {name: color for name, color in zip(spectrum_names, spectrum_colors)}

    def shade(self, token: ColorTokenType, shade: ColorShadeType = 500) -> str:
        """Get a specific color shade from the spectrum."""
        return self.spectrum(token)[shade]

    def hovered(self, token: ColorTokenType):
        """Boostrap style hover color"""
        return self.state_color(token, "hover")

    def pressed(self, token: ColorTokenType):
        """Bootstrap style pressed color"""
        return self.state_color(token, "active")

    def focused(self, token: ColorTokenType) -> str:
        """Bootstrap-style focus color (darken 18%)"""
        return self.state_color(token, 'focus')

    def focused_border(self, token: ColorTokenType) -> str:
        """Inner border color on focus (slightly adjusted for visibility)."""
        base = self.color(token)
        lum = relative_luminance(base)
        if self.mode == "dark":
            # Lighten for dark tokens in dark theme
            return lighten_color(base, 0.1)
        else:
            # Darken in light theme
            return darken_color(base, 0.2 if lum > 0.5 else 0.1)

    def focused_ring(self, token: ColorTokenType) -> str:
        """Return a focus ring color with good contrast for the theme mode.

        Light theme:
            - Darken and mix with surface to create contrast.
        Dark theme:
            - Lighten and mix with surface to create contrast.
        """
        base = self.focused(token)
        surface = self.surface_base()
        lum = relative_luminance(base)

        if self.mode == "dark":
            # Brighten low-luminance colors for contrast on dark backgrounds
            if lum < 0.3:
                mixed = mix_colors(lighten_color(base, 0.2), surface, 0.2)
            else:
                mixed = mix_colors(base, surface, 0.3)
        else:
            # Darken high-luminance colors for contrast on light backgrounds
            if lum > 0.5:
                mixed = darken_color(mix_colors(base, surface, 0.2), 0.15)
            else:
                mixed = mix_colors(lighten_color(base, 0.25), surface, 0.25)

        return mixed

    def state_color(self, token: ColorTokenType, state: Literal["hover", "active", "focus"]) -> str:
        """Return an adjusted button background color based on state and luminance.

        Bootstrap lightens or darkens depending on base brightness:
        - Light buttons darken on hover/active
        - Dark buttons lighten on hover/active
        """
        base = self.color(token)
        if state == "focus":
            return base

        delta = {
            "hover": 0.08,
            "active": 0.12,
            "focus": 0.08
        }[state]
        lum = relative_luminance(base)
        if lum < 0.5:
            return lighten_color(base, delta)
        return darken_color(base, delta)

    def disabled(self, token: ColorTokenType) -> str:
        return self.spectrum(token)[300 if self.mode == "light" else 700]

    def border(self, token: ColorTokenType) -> str:
        """Get the color for a border (Bootstrap-style: darken 20%)"""
        base = self.color(token)
        return darken_color(base, 0.20)

    def emphasis(self, token: ColorTokenType) -> str:
        """Get an emphasis color."""
        base = self.color(token)
        return shade_color(base, 0.60) if self.mode == "light" else shade_color(base, 0.30)

    def surface_color(self, role: SurfaceRoleType) -> str:
        """Return the surface color based on role"""
        return {
            "base": self.surface_base(),
            "muted": self.surface_muted(),
            "subtle": self.surface_subtle(),
            "emphasis": self.surface_emphasis(),
            "accent": self.surface_accent(),
            "inverse": self.surface_inverse(),
            "overlay": self.surface_overlay(),
        }.get(role, self.surface_base())

    def surface_base(self) -> str:
        """Main surface (application background)."""
        return self.color("background")

    def surface_muted(self) -> str:
        """Muted surface for content containers (cards, list rows)."""
        bg = self.color("background")
        return shade_color(bg, 0.97) if self.mode == "light" else tint_color(bg, 0.07)

    def surface_subtle(self) -> str:
        """Subtle elevation layer for grouped content."""
        bg = self.color("background")
        return shade_color(bg, 0.94) if self.mode == "light" else tint_color(bg, 0.10)

    def surface_emphasis(self) -> str:
        """Stronger surface for modals and foreground containers."""
        bg = self.color("background")
        return shade_color(bg, 0.88) if self.mode == "light" else tint_color(bg, 0.20)

    def surface_accent(self) -> str:
        """Accent surface based on primary role color."""
        base = self.color("primary")
        return tint_color(base, 0.15) if self.mode == "light" else tint_color(base, 0.65)

    def surface_inverse(self) -> str:
        """Surface with inverted background (e.g., footer or nav)."""
        return self.color("foreground")

    def surface_overlay(self) -> str:
        """Overlay surface for dimming or modals."""
        return "#00000080" if self.mode == "light" else "#FFFFFF33"

    def on_color(self, token: ColorTokenType) -> str:
        """Get a foreground color with best contrast for the given token background."""
        bg = self.color(token)
        return best_foreground(bg, self.color("background"), self.color("foreground"))

    def on_surface(self) -> str:
        """Get the default foreground color for content on the background surface."""
        return best_foreground(self.color("background"))

    def on_surface_medium(self) -> str:
        """Get a muted foreground color for medium emphasis content."""
        base = self.color("foreground")
        return tint_color(base, 0.5 if self.mode == "light" else 1.5)

    def on_surface_disabled(self) -> str:
        """Get a disabled foreground color for content on surfaces."""
        base = self.color("foreground")
        return tint_color(base, 0.9 if self.mode == "light" else 0.1)

    def on_surface_inverse(self) -> str:
        """Get an inverse foreground color for surfaces with strong backgrounds."""
        return best_foreground(self.color("background"))

    def __repr__(self):
        return f"<Theme name={self.name} mode={self.mode}>"


load_default_themes()
