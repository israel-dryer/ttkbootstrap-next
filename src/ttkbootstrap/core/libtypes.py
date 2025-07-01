from typing import Literal, Union

BindScopeType = Literal['all', 'class', 'widget']
TraceOperationType = Literal["array", "read", "write", "unset"]
ColorTokenType = Literal[
    'primary', 'secondary', 'success', 'info', 'warning', 'danger',
    'dark', 'light', 'blue', 'indigo', 'purple', 'red', 'orange',
    'yellow', 'green', 'teal', 'cyan', 'white', 'black', 'gray',
    'foreground', 'background'
]
SurfaceRoleType = Literal['base', 'muted', 'subtle', 'emphasis', 'accent', 'inverse', 'overlay']
ColorShadeType = Literal[100, 200, 300, 400, 500, 600, 700, 800, 900]
ColorThemeType = Union[Literal['light', 'dark'], str]
ColorModelType = Literal['hex', 'hsl', 'rgb']