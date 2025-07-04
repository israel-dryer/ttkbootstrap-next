from tkinter.font import Font
from typing import Literal, Union

ButtonVariant = Literal['solid', 'outline', 'ghost']

ButtonColorToken = Literal['primary', 'secondary', 'success', 'info', 'warning', 'danger', 'light', 'dark']
SeparatorColorToken = Literal['border', 'primary', 'secondary', 'success', 'info', 'warning', 'danger', 'light', 'dark']

SurfaceToken = Literal[
    'base', 'primary', 'secondary', 'success', 'info', 'warning', 'danger', 'light', 'dark',
    'primary-subtle', 'secondary-subtle', 'success-subtle', 'info-subtle', 'warning-subtle', 'danger-subtle',
    'light-subtle', 'dark-subtle', 'base-subtle',
    'layer-1', 'layer-2', 'layer-3', 'layer-4', 'layer-5',
    'blue-100', 'blue-200', 'blue-300', 'blue-400', 'blue-500', 'blue-600', 'blue-700', 'blue-800', 'blue-900',
    'indigo-100', 'indigo-200', 'indigo-300', 'indigo-400', 'indigo-500', 'indigo-600', 'indigo-700', 'indigo-800', 'indigo-900',
    'purple-100', 'purple-200', 'purple-300', 'purple-400', 'purple-500', 'purple-600', 'purple-700', 'purple-800',
    'purple-900', 'red-100', 'red-200', 'red-300', 'red-400', 'red-500', 'red-600', 'red-700', 'red-800', 'red-900',
    'orange-100', 'orange-200', 'orange-300', 'orange-400', 'orange-500', 'orange-600', 'orange-700', 'orange-800',
    'orange-900', 'yellow-100', 'yellow-200', 'yellow-300', 'yellow-400', 'yellow-500', 'yellow-600', 'yellow-700', 'yellow-800',
    'yellow-900', 'green-100', 'green-200', 'green-300', 'green-400', 'green-500', 'green-600', 'green-700', 'green-800', 'green-900',
    'teal-100', 'teal-200', 'teal-300', 'teal-400', 'teal-500', 'teal-600', 'teal-700', 'teal-800', 'teal-900',
    'cyan-100', 'cyan-200', 'cyan-300', 'cyan-400', 'cyan-500', 'cyan-600', 'cyan-700', 'cyan-800', 'cyan-900',
    'gray-100', 'gray-200', 'gray-300', 'gray-400', 'gray-500', 'gray-600', 'gray-700', 'gray-800', 'gray-900',
]

ForegroundToken = Literal[
    'foreground', 'primary', 'secondary', 'success', 'info', 'warning', 'danger', 'light', 'dark',
    'primary-subtle', 'secondary-subtle', 'success-subtle', 'info-subtle', 'warning-subtle', 'danger-subtle',
    'light-subtle', 'dark-subtle', 'base-subtle',
    'blue-100', 'blue-200', 'blue-300', 'blue-400', 'blue-500', 'blue-600', 'blue-700', 'blue-800', 'blue-900',
    'indigo-100', 'indigo-200', 'indigo-300', 'indigo-400', 'indigo-500', 'indigo-600', 'indigo-700', 'indigo-800', 'indigo-900',
    'purple-100', 'purple-200', 'purple-300', 'purple-400', 'purple-500', 'purple-600', 'purple-700', 'purple-800',
    'purple-900', 'red-100', 'red-200', 'red-300', 'red-400', 'red-500', 'red-600', 'red-700', 'red-800', 'red-900',
    'orange-100', 'orange-200', 'orange-300', 'orange-400', 'orange-500', 'orange-600', 'orange-700', 'orange-800',
    'orange-900', 'yellow-100', 'yellow-200', 'yellow-300', 'yellow-400', 'yellow-500', 'yellow-600', 'yellow-700', 'yellow-800',
    'yellow-900', 'green-100', 'green-200', 'green-300', 'green-400', 'green-500', 'green-600', 'green-700', 'green-800', 'green-900',
    'teal-100', 'teal-200', 'teal-300', 'teal-400', 'teal-500', 'teal-600', 'teal-700', 'teal-800', 'teal-900',
    'cyan-100', 'cyan-200', 'cyan-300', 'cyan-400', 'cyan-500', 'cyan-600', 'cyan-700', 'cyan-800', 'cyan-900',
    'gray-100', 'gray-200', 'gray-300', 'gray-400', 'gray-500', 'gray-600', 'gray-700', 'gray-800', 'gray-900',
]

ThemeColorToken = Literal[
    'primary', 'secondary', 'success', 'info', 'warning', 'danger',
    'dark', 'light', 'blue', 'indigo', 'purple', 'red', 'orange',
    'yellow', 'green', 'teal', 'cyan', 'white', 'black', 'gray',
    'foreground', 'background'
]

BootstrapFontType = Literal[
    'label', 'body', 'body-sm', 'body-lg', 'body-xl', 'caption',
    'display-xl', 'display-lg', 'heading-xl', 'heading-lg', 'heading-md', 'code'
]

FontTokenType = Union[BootstrapFontType, str, Font]
