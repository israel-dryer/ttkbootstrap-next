import json
import importlib.resources as resources
from typing import Optional, Union, Literal, cast

from .utils import (
    darken_color, tint_color, shade_color, relative_luminance, best_foreground,
    lighten_color, mix_colors
)
from ..core.libtypes import ColorShade
from .tokens import ThemeColor, SurfaceColor, ForegroundColor
from ..exceptions import InvalidThemeError, InvalidTokenError

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


TINT_WEIGHTS = (0.80, 0.60, 0.40, 0.25)
SHADE_WEIGHTS = (0.25, 0.4, 0.6, 0.85)

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

    def color(self, token: ThemeColor) -> str:
        """Get the hex value of a token."""
        return self.tokens.get(token)

    def elevate_surface(self, token: ThemeColor, elevation: int = 0, *, max_elevation: int = 5) -> str:
        """
        Adjust a surface background color for elevation:
        - Light themes: blend darker
        - Dark themes: blend lighter

        Args:
            token: The base background color.
            elevation: Elevation level (0 = no change).
            max_elevation: Max elevation to normalize blending.

        Returns:
            Hex color string of the elevated surface.
        """
        if elevation <= 0:
            return self.color(token)

        # Determine blend target based on theme mode
        blend_target = "#000000" if self.mode == "light" else "#ffffff"

        # Elevation weight — adjust this curve to taste
        weight = min(elevation / max_elevation, 1.0) * 0.3  # up to 30% blend
        return mix_colors(blend_target, self.color(token), weight)

    def spectrum(self, token: ThemeColor) -> dict[int, str]:
        """Get the full color spectrum (tints, base, shades) for a token."""
        base = self.color(token)
        spectrum_names = [100, 200, 300, 400, 500, 600, 700, 800, 900]
        tints = [tint_color(base, w) for w in TINT_WEIGHTS]
        shades = [shade_color(base, w) for w in SHADE_WEIGHTS]
        spectrum_colors = [*tints, base, *shades]
        return {name: color for name, color in zip(spectrum_names, spectrum_colors)}

    def shade(self, token: ThemeColor, shade: ColorShade = 500) -> str:
        """Get a specific color shade from the spectrum."""
        return self.spectrum(token)[shade]

    def hovered(self, token: ThemeColor):
        """Boostrap style hover color"""
        return self.state_color(token, "hover")

    def pressed(self, token: ThemeColor):
        """Bootstrap style pressed color"""
        return self.state_color(token, "active")

    def focused(self, token: ThemeColor) -> str:
        """Bootstrap-style focus color (darken 18%)"""
        return self.state_color(token, 'focus')

    def focused_border(self, token: ThemeColor) -> str:
        """Inner border color on focus (slightly adjusted for visibility)."""
        base = self.color(token)
        lum = relative_luminance(base)
        if self.mode == "dark":
            # Lighten for dark tokens in dark theme
            return lighten_color(base, 0.1)
        else:
            # Darken in light theme
            return darken_color(base, 0.2 if lum > 0.5 else 0.1)

    def focused_ring(
            self,
            token: ThemeColor,
            surface: str | None = None
    ) -> str:
        """
        Return a focus ring color with good contrast against the surface background.

        In light mode:
            - High-luminance colors are darkened and mixed with surface.
            - Low-luminance colors are lightened and blended for subtlety.

        In dark mode:
            - Low-luminance colors are brightened and blended.
            - High-luminance colors are softly mixed for contrast.

        Args:
            token: Theme color token used as the base for focus color.
            surface: Optional hex surface background color. Defaults to self.surface_base().
        """
        base = self.focused(token)
        surface = surface or self.surface_base()
        lum = relative_luminance(base)

        if self.mode == "dark":
            if lum < 0.3:
                brightened = lighten_color(base, 0.2)
                mixed = mix_colors(brightened, surface, 0.2)
            else:
                mixed = mix_colors(base, surface, 0.3)
        else:
            if lum > 0.5:
                blended = mix_colors(base, surface, 0.2)
                mixed = darken_color(blended, 0.15)
            else:
                brightened = lighten_color(base, 0.25)
                mixed = mix_colors(brightened, surface, 0.25)

        return mixed

    def subtle(
            self,
            token: ThemeColor,
            surface: SurfaceColor = "base"
    ) -> str:
        """
        Return a subtle background color for the given token.

        This is used for low-emphasis states like ghost button hovers,
        and should blend naturally with the given surface.

        Args:
            token: The semantic theme color token.
            surface: The surface token (e.g., "base", "raised", "sunken") to blend with.
        """
        base_color = self.color(token)
        surface_color = self.surface_color(surface)

        if self.mode == "light":
            # Blend mostly with surface color for subtle hover effect
            return mix_colors(base_color, surface_color, 0.08)
        else:
            # In dark mode, keep similar strategy but more visible token hint
            return mix_colors(base_color, surface_color, 0.10)

    def state_color(self, token: ThemeColor, state: Literal["hover", "active", "focus"]) -> str:
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

    def disabled(self, token: ThemeColor) -> str:
        return self.spectrum(token)[300 if self.mode == "light" else 700]

    def border(self, token: ThemeColor) -> str:
        """Get the color for a border (Bootstrap-style: darken 20%)"""
        base = self.color(token)
        return darken_color(base, 0.20)

    def border_on_surface(self, surface_color: str):
        """Get a border color that contrast against the surface"""
        if self.mode == "dark":
            return lighten_color(surface_color, 0.20)
        else:
            return darken_color(surface_color, 0.20)

    def surface_color(self, token: SurfaceColor = "base") -> str:
        """Return the surface color"""
        token = token.replace('base', 'background')
        try:
            if 'subtle' in token:
                color, _ = token.split('-')
                return self.subtle(cast(ThemeColor, color))
            if 'layer' in token:
                _, elevation = token.split('-')
                return self.elevate_surface("background", int(elevation))
            if '-' in token:
                color, scale = token.split('-')
                return self.spectrum(color)[int(scale)]
            if token == "base":
                return self.surface_base()
            return self.color(cast(ThemeColor, token))
        except Exception as e:
            raise InvalidTokenError(str(e), token)

    def foreground_color(self, token: ForegroundColor):
        try:
            if 'subtle' in token:
                color, _ = token.split('-')
                return self.subtle(cast(ThemeColor, color))
            if '-' in token:
                color, scale = token.split('-')
                return self.spectrum(color)[int(scale)]
            return self.color(cast(ThemeColor, token))
        except Exception as e:
            raise InvalidTokenError(str(e), token)

    def surface_base(self) -> str:
        """Main surface (application background)."""
        return self.color("background")

    def on_color(self, token: ThemeColor) -> str:
        """Get a foreground color with the best contrast for the given token background."""
        bg = self.color(token)
        return best_foreground(bg, [self.color('foreground'), self.color('background')])

    def on_surface(self, token: SurfaceColor = "base") -> str:
        color = self.surface_color(token)
        return best_foreground(color, [self.color('foreground'), self.color('background')])

    def on_surface_disabled(self) -> str:
        """Get a disabled foreground color for content on surfaces."""
        base = self.color("foreground")
        return tint_color(base, 0.9 if self.mode == "light" else 0.1)

    def on_surface_inverse(self) -> str:
        """Get an inverse foreground color for surfaces with strong backgrounds."""
        return best_foreground(self.color("background"), [self.color('foreground'), self.color('background')])

    def __repr__(self):
        return f"<Theme name={self.name} mode={self.mode}>"


load_default_themes()
