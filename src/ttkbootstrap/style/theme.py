import json
import importlib.resources as resources
from typing import Literal

from PIL import ImageColor


def load_json(filename: str, package: str = "ttkbootstrap.assets.themes") -> dict:
    """Load a JSON file from the given package.

    Args:
        filename: The name of the JSON file.
        package: The package containing the file.

    Returns:
        A dictionary of the parsed JSON data.
    """
    with resources.files(package).joinpath(filename).open("r", encoding="utf-8") as f:
        return json.load(f)


def mix_colors(color1: str, color2: str, weight: float) -> str:
    """Mix two colors by weight.

    Args:
        color1: The foreground color in hex format (e.g., '#FF0000').
        color2: The background color in hex format.
        weight: A float from 0 to 1, where 1 favors color1 and 0 favors color2.

    Returns:
        A hex color string representing the mixed result.
    """
    r1, g1, b1 = ImageColor.getrgb(color1)
    r2, g2, b2 = ImageColor.getrgb(color2)

    r = round(r1 * weight + r2 * (1 - weight))
    g = round(g1 * weight + g2 * (1 - weight))
    b = round(b1 * weight + b2 * (1 - weight))

    return f"#{r:02X}{g:02X}{b:02X}"


def tint_color(color: str, base_weight: float) -> str:
    """Tint a color by mixing it with white.

    Args:
        color: The base color in hex.
        base_weight: Amount of base color to retain (0–1).

    Returns:
        A tinted hex color string.
    """
    return mix_colors("#ffffff", color, base_weight)


def shade_color(color: str, base_weight: float) -> str:
    """Shade a color by mixing it with black.

    Args:
        color: The base color in hex.
        base_weight: Amount of base color to retain (0–1).

    Returns:
        A shaded hex color string.
    """
    return mix_colors("#000000", color, base_weight)


def relative_luminance(hex_color: str) -> float:
    """Calculate the relative luminance of a color.

    Args:
        hex_color: A hex color string.

    Returns:
        The luminance value from 0 (black) to 1 (white).
    """
    r, g, b = [x / 255 for x in ImageColor.getrgb(hex_color)]

    def adjust(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = adjust(r), adjust(g), adjust(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(color1: str, color2: str) -> float:
    """Calculate the contrast ratio between two colors.

    Args:
        color1: First hex color.
        color2: Second hex color.

    Returns:
        The contrast ratio as a float.
    """
    lum1 = relative_luminance(color1)
    lum2 = relative_luminance(color2)
    l1, l2 = max(lum1, lum2), min(lum1, lum2)
    return (l1 + 0.05) / (l2 + 0.05)


def best_foreground(bg_color: str, light: str = "#ffffff", dark: str = "#000000") -> str:
    """Determine which foreground color has better contrast on a background.

    Args:
        bg_color: The background color in hex.
        light: A light foreground candidate.
        dark: A dark foreground candidate.

    Returns:
        The color with better contrast (either `light` or `dark`).
    """
    contrast_light = contrast_ratio(bg_color, light)
    contrast_dark = contrast_ratio(bg_color, dark)
    return light if contrast_light > contrast_dark else dark


ColorTokenType = Literal[
    'primary', 'secondary', 'success', 'info', 'warning', 'danger',
    'dark', 'light', 'blue', 'indigo', 'purple', 'red', 'orange',
    'yellow', 'green', 'teal', 'cyan', 'white', 'black', 'gray',
    'foreground', 'background'
]

SurfaceRoleType = Literal['base', 'muted', 'subtle', 'emphasis', 'accent', 'inverse', 'overlay']

ColorShadeType = Literal[100, 200, 300, 400, 500, 600, 700, 800, 900]

ColorProgression = (0.80, 0.60, 0.40, 0.20)


class ColorTheme:
    """Encapsulates theme tokens and provides utilities for derived color states."""

    def __init__(self, theme: dict):
        """Initialize the theme from a token dictionary.

        Args:
            theme: A dictionary containing 'name', 'mode', and 'colors'.
        """
        self.name = theme.get("name", "Unknown")
        self.mode = theme.get("mode", "light")
        self.tokens = theme.get("colors", {})

    def color(self, token: ColorTokenType) -> str:
        """Get the hex value of a token."""
        return self.tokens.get(token)

    def spectrum(self, token: ColorTokenType) -> dict[int, str]:
        """Get the full color spectrum (tints, base, shades) for a token."""
        base = self.color(token)
        spectrum_names = [100, 200, 300, 400, 500, 600, 700, 800, 900]
        tints = [tint_color(base, w) for w in ColorProgression]
        shades = [shade_color(base, w) for w in reversed(ColorProgression)]
        spectrum_colors = [*tints, base, *shades]
        return {name: color for name, color in zip(spectrum_names, spectrum_colors)}

    def shade(self, token: ColorTokenType, shade: ColorShadeType = 500) -> str:
        """Get a specific color shade from the spectrum."""
        return self.spectrum(token)[shade]

    def subtle(self, token: ColorTokenType) -> str:
        """Get a subtle background tint for the token."""
        base = self.color(token)
        return tint_color(base, 0.20 if self.mode == "light" else 0.85)

    def hovered(self, token: ColorTokenType) -> str:
        """Get the color for a hovered state."""
        base = self.color(token)
        return shade_color(base, 0.90) if self.mode == "light" else tint_color(base, 0.60)

    def pressed(self, token: ColorTokenType) -> str:
        """Get the color for a pressed state."""
        base = self.color(token)
        return shade_color(base, 0.80) if self.mode == "light" else tint_color(base, 0.40)

    def focused(self, token: ColorTokenType) -> str:
        """Get the color for a focus ring."""
        base = self.color(token)
        return tint_color(base, 0.50) if self.mode == "light" else tint_color(base, 0.80)

    def disabled(self, token: ColorTokenType) -> str:
        """Get the color for a disabled state."""
        base = self.color(token)
        return tint_color(base, 0.70) if self.mode == "light" else shade_color(base, 0.50)

    def border(self, token: ColorTokenType) -> str:
        """Get the color for a border."""
        base = self.color(token)
        return tint_color(base, 0.30) if self.mode == "light" else tint_color(base, 0.60)

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
        return tint_color(base, 0.7 if self.mode == "light" else 0.4)

    def on_surface_inverse(self) -> str:
        """Get an inverse foreground color for surfaces with strong backgrounds."""
        return best_foreground(self.color("background"))
