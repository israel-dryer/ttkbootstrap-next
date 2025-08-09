from typing import Literal, Union

ColorShade = Literal[100, 200, 300, 400, 500, 600, 700, 800, 900]
ColorMode = Union[Literal['light', 'dark'], str]
ColorModel = Literal['hex', 'hsl', 'rgb']
ButtonSize = Literal['sm', 'md', 'lg']
