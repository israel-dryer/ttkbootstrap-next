"""
This module provides a modern, semantic typography system aligned with
Microsoft Fluent 2's type scale.

It defines scalable font tokens such as `display_xl`, `heading_md`, and `body_sm`,
ensuring consistent font usage across platforms and widgets.

Key Features:
-------------
- Fluent 2-based font sizes and weights
- Semantic tokens for display, heading, body, label, caption, and monospace code
- Platform fallback support for missing fonts
- Auto-registration with Tk named fonts
"""

import platform
from tkinter.font import Font
from typing import Literal, NamedTuple
from tkinter import Misc, font


class FontSpec(NamedTuple):
    """Semantic font definition with metadata."""
    font: str
    size: int
    weight: Literal['normal', 'bold']
    line_height: int


class FontTokenNames:
    """All predefined font token names used in Fluent 2 typography."""
    display_xl: str = "display-xl"
    display_lg: str = "display-lg"
    heading_xl: str = "heading-xl"
    heading_lg: str = "heading-lg"
    heading_md: str = "heading-md"
    body_xl: str = "body-xl"
    body_lg: str = "body-lg"
    body: str = "body"
    body_sm: str = "body-sm"
    label: str = "label"
    caption: str = "caption"
    code: str = "code"


class FontTokens(NamedTuple):
    display_xl: FontSpec
    display_lg: FontSpec
    heading_xl: FontSpec
    heading_lg: FontSpec
    heading_md: FontSpec
    body_xl: FontSpec
    body_lg: FontSpec
    body: FontSpec
    body_sm: FontSpec
    label: FontSpec
    caption: FontSpec
    code: FontSpec


def system_fallback_font() -> str:
    """Determine fallback UI font based on current platform."""
    return {
        "Windows": "Segoe UI",
        "Darwin": "San Francisco",  # Tk may resolve to Helvetica internally
    }.get(platform.system(), "Ubuntu")


def system_monospace_font() -> str:
    """Determine fallback monospace font based on current platform."""
    return {
        "Windows": "Consolas",
        "Darwin": "Menlo",
    }.get(platform.system(), "DejaVu Sans Mono")


FALLBACK_FONT = system_fallback_font()
FALLBACK_MONO = system_monospace_font()

DEFAULT_FONT_TOKENS = FontTokens(
    display_xl=FontSpec("Segoe UI", 24, "bold", 48),
    display_lg=FontSpec("Segoe UI", 20, "bold", 40),
    heading_xl=FontSpec("Segoe UI", 16, "bold", 32),
    heading_lg=FontSpec("Segoe UI", 14, "bold", 28),
    heading_md=FontSpec("Segoe UI", 12, "bold", 24),
    body_sm=FontSpec("Segoe UI", 10, "normal", 14),
    body=FontSpec("Segoe UI", 11, "normal", 16),
    body_lg=FontSpec("Segoe UI", 12, "normal", 18),
    body_xl=FontSpec("Segoe UI", 13, "normal", 20),
    label=FontSpec("Segoe UI", 9, "bold", 14),
    caption=FontSpec("Segoe UI", 8, "normal", 12),
    code=FontSpec("Consolas", 10, "normal", 14),
)

TK_FONT_OVERRIDES = {
    "TkDefaultFont": "body-lg",
    "TkTextFont": "body",
    "TkHeadingFont": "heading-md",
    "TkCaptionFont": "caption",
    "TkFixedFont": "code",
}


class Typography:
    """
    Typography engine for defining and registering semantic font tokens.

    Handles font customization, fallback behavior, Tk alias overrides,
    and named font registration.
    """

    _fonts: FontTokens = DEFAULT_FONT_TOKENS
    _use_fallback: bool = False
    _root: Misc
    _named_fonts: dict[str, Font] = {}

    @classmethod
    def use_fonts(cls, fonts: FontTokens = DEFAULT_FONT_TOKENS, *, fallback: bool = False) -> None:
        """Apply and register a complete font token set."""
        cls._fonts = fonts
        cls._use_fallback = fallback
        cls._register_fonts()
        cls._override_tk_fonts()

    @classmethod
    def set_global_family(cls, family: str) -> None:
        """Update all font tokens to use a single font family (except monospace)."""
        updated = {
            name: FontSpec(
                family if name != "code" else cls._fonts.code.font,
                spec.size, spec.weight, spec.line_height
            )
            for name, spec in cls._fonts._asdict().items()
        }
        cls.use_fonts(FontTokens(**updated), fallback=True)

    @classmethod
    def update_font_token(cls, name: str, **kwargs) -> None:
        """Update fields of an existing font token."""
        old = cls.get_token(name)
        updated = old._replace(**kwargs)
        attr_name = name.replace("-", "_")
        setattr(cls._fonts, attr_name, updated)
        cls._register_fonts()
        if name in TK_FONT_OVERRIDES.values():
            cls._override_tk_fonts()

    @classmethod
    def get_token(cls, name: str) -> FontSpec:
        """Retrieve a font spec by token name."""
        attr = name.replace("-", "_")
        return getattr(cls._fonts, attr, cls._fonts.body)

    @classmethod
    def get_font(cls, name: str) -> Font:
        """Return a `Font` object for a semantic token."""
        spec = cls.get_token(name)
        fallback = FALLBACK_MONO if name == "code" else FALLBACK_FONT
        return Font(
            name=name,
            family=spec.font if not cls._use_fallback else fallback,
            size=spec.size,
            weight=spec.weight,
        )

    @classmethod
    def all(cls) -> FontTokens:
        """Return the current set of registered font tokens."""
        return cls._fonts

    @classmethod
    def _register_fonts(cls) -> None:
        """Register each semantic token as a named font if not already present."""
        token_map = {k: v for k, v in FontTokenNames.__dict__.items() if not k.startswith("__")}
        for field_name in cls._fonts._fields:
            spec = getattr(cls._fonts, field_name)
            font_name = token_map.get(field_name, field_name)  # field_name → "body-lg", etc.
            fallback = FALLBACK_MONO if field_name == "code" else FALLBACK_FONT
            f = Font(
                name=font_name,
                family=spec.font if not cls._use_fallback else fallback,
                size=spec.size,
                weight=spec.weight,
            )
            cls._named_fonts[font_name] = f

    @classmethod
    def _override_tk_fonts(cls) -> None:
        """Update Tkinter's default fonts to use semantic tokens."""
        for tk_name, token_name in TK_FONT_OVERRIDES.items():
            spec = cls.get_token(token_name)
            fallback = FALLBACK_MONO if token_name == "code" else FALLBACK_FONT
            if tk_name in font.names():
                font.nametofont(tk_name).configure(
                    family=spec.font if not cls._use_fallback else fallback,
                    size=spec.size,
                    weight=spec.weight,
                )
