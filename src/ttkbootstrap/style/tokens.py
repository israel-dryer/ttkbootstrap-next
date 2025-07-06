from tkinter.font import Font
from typing import Literal, Union

ButtonVariant = Literal['solid', 'outline', 'ghost']

# === Color Types ===

# supports subtle variants, e.g., 'primary-subtle'
SemanticColor = Literal['primary', 'secondary', 'success', 'info', 'warning', 'danger', 'light', 'dark']
LayerColor = Literal['layer-1', 'layer-2', 'layer-3', 'layer-4', 'layer-5']
UtilityColor = Literal['foreground', 'background']

# supports shade variants 100-900
ShadeColor = Literal['blue', 'indigo', 'purple', 'red', 'orange', 'yellow', 'green', 'teal', 'cyan', 'gray']

# === Color Tokens ===

SurfaceToken = Union[LayerColor, SemanticColor, str]
ForegroundToken = Union[SemanticColor, ShadeColor, UtilityColor, str]
ThemeColorToken = Union[SemanticColor, ShadeColor, UtilityColor]
ButtonColorToken = SemanticColor
SeparatorColorToken = Union[Literal['border'], SemanticColor]

# === Font Tokens ====

BootstrapFontType = Literal[
    'label', 'body', 'body-sm', 'body-lg', 'body-xl', 'caption',
    'display-xl', 'display-lg', 'heading-xl', 'heading-lg', 'heading-md', 'code'
]

FontTokenType = Union[BootstrapFontType, str, Font]
