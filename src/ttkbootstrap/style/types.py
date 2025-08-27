from tkinter.font import Font
from typing import Literal, Union

ColorShade = Literal[100, 200, 300, 400, 500, 600, 700, 800, 900]
ColorMode = Union[Literal['light', 'dark'], str]
ColorModel = Literal['hex', 'hsl', 'rgb']
ButtonSize = Literal['sm', 'md', 'lg']
ButtonVariant = Literal['solid', 'outline', 'ghost', 'text', 'list']

# === Color Types ===

# supports subtle variants, e.g., 'primary-subtle'
SemanticColor = Literal['primary', 'secondary', 'success', 'info', 'warning', 'danger', 'light', 'dark']
LayerColor = Literal['layer-1', 'layer-2', 'layer-3', 'layer-4', 'layer-5']
UtilityColor = Literal['foreground', 'background']

# supports shade variants 100-900
ShadeColor = Literal['blue', 'indigo', 'purple', 'red', 'orange', 'yellow', 'green', 'teal', 'cyan', 'gray']

# === Color Tokens ===

SurfaceColor = Union[LayerColor, SemanticColor, str]
ForegroundColor = Union[SemanticColor, ShadeColor, UtilityColor, str]
ThemeColor = Union[SemanticColor, ShadeColor, UtilityColor, str]
SeparatorColor = Union[Literal['border'], SemanticColor]
BorderColor = Union[Literal['border'], SemanticColor, ShadeColor, str]

# === Font Tokens ====

BootstrapFontType = Literal[
    'label', 'body', 'body-sm', 'body-lg', 'body-xl', 'caption',
    'display-xl', 'display-lg', 'heading-xl', 'heading-lg', 'heading-md', 'code'
]

TypographyToken = Union[BootstrapFontType, str, Font]