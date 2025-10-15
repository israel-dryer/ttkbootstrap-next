import tomllib
from importlib import resources

from ttkbootstrap.exceptions import InvalidThemeError
from ttkbootstrap.style.utils import shade_color, tint_color

_registered_themes = {}
_current_theme = None
_theme_provider = None

TINT_WEIGHTS = (0.80, 0.60, 0.40, 0.25)
SHADE_WEIGHTS = (0.25, 0.4, 0.6, 0.85)


def register_user_theme(name, path):
    data = load_user_defined_theme(path)
    _registered_themes[name] = data


def get_theme(name):
    if name in _registered_themes:
        return _registered_themes[name]
    else:
        raise InvalidThemeError(f"Theme '{name}' is not registered")


def load_system_themes():
    for theme in ["dark.toml", "light.toml"]:
        data = load_package_theme(theme)
        name = data["name"]
        _registered_themes[name] = data


def load_user_defined_theme(path):
    with open(path, "rb") as f:
        return tomllib.load(f)


def load_package_theme(filename: str, package="ttkbootstrap.assets.themes"):
    with resources.files(package).joinpath(filename).open("rb") as f:
        return tomllib.load(f)


def color_spectrum(token, value):
    spectrum_names = [f'{token}-{x}' for x in [100, 200, 300, 400, 500, 600, 700, 800, 900]]
    tints = [tint_color(value, w) for w in TINT_WEIGHTS]
    shades = [shade_color(value, w) for w in SHADE_WEIGHTS]
    spectrum_colors = [*tints, value, *shades]
    return {name: color for name, color in zip(spectrum_names, spectrum_colors)}


class ThemeProvider:

    def __init__(self, name: str = "light"):
        self._theme = {}
        self._colors = {}
        load_system_themes()
        self.use(name)

    def use(self, name):
        self._theme = get_theme(name)
        self.build_theme_colors()
        self.update_theme_styles()

    @staticmethod
    def update_theme_styles():
        """Trigger a style update for the active theme"""
        from tkinter.ttk import Style
        Style().theme_use('clam')

    @staticmethod
    def instance(name="light"):
        global _theme_provider
        if _theme_provider is None:
            _theme_provider = ThemeProvider()
            _theme_provider.use(name)
        return _theme_provider

    def build_theme_colors(self):
        colors = {}
        colors.update(
            foreground=self._palette.get('foreground'),
            background=self._palette.get('background'),
            white=self._palette.get('white'),
            black=self._palette.get('black'),
            **self._shades,
        )
        # add shaded spectrum
        for color, value in self._shades.items():
            colors.update(**color_spectrum(color, value))

        # sematic tokens
        for token, value in self._semantic.items():
            colors[token] = colors[value]

        self._colors.clear()
        self._colors.update(**colors)

    @property
    def theme(self):
        return self._theme

    @property
    def name(self):
        return self.theme.get('name')

    @property
    def mode(self):
        return self.theme.get('mode')

    @property
    def _palette(self):
        return self.theme.get('palette')

    @property
    def _shades(self):
        return self._palette.get('shades')

    @property
    def _semantic(self):
        return self._palette.get('semantic')

    @property
    def typography(self):
        return self.theme.get('typography')

    @property
    def components(self):
        return self._palette.get('components')

    @property
    def colors(self):
        return self._colors

    def __repr__(self):
        """Return a string representation of the current theme"""
        return f"<Theme name={self.name}> mode={self.mode}>"
