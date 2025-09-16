from __future__ import annotations

from tkinter import ttk
from tkinter.font import Font
from typing import Callable, Literal, Union

from ttkbootstrap.localization.intl_format import FormatSpec
from ttkbootstrap.types import CoreOptions, Justify, Padding

DialogType = Literal[
    'openfilename', 'openfile', 'directory', 'openfilenames', 'openfiles',
    'saveasfile', 'saveasfilename'
]


class EntryOptions(CoreOptions, total=False):
    cursor: str
    font: str | Font
    foreground: str
    take_focus: bool
    x_scroll_command: Callable
    export_selection: bool
    justify: Justify
    show: str
    width: int
    padding: Padding


class TextEntryOptions(EntryOptions, total=False):
    required: bool
    display_format: FormatSpec
    allow_blank: bool


class NumberEntryOptions(EntryOptions, total=False):
    required: bool


Index = Union[int, str]
EntryLike = Union[ttk.Entry, ttk.Spinbox]


class SpinboxOptions(CoreOptions, total=False):
    """
    Options for configuring a number spinner widget.

    Attributes:
        cursor: The cursor that appears when the mouse is over the widget.
        font: The font used to render text in the entry (name or Font object).
        foreground: The text color (e.g., "#333", "red").
        take_focus: Indicates whether the widget accepts focus during keyboard traversal.
        x_scroll_command: A callback used to link the entry to a horizontal scrollbar.
        export_selection: Whether to export the selection to the clipboard (default is True).
        justify: Text justification (left, center, or right).
        show: The character used to mask text (e.g., "*" for passwords).
        width: The width of the entry widget in characters.
    """
    cursor: str
    font: str | Font
    foreground: str
    take_focus: bool
    x_scroll_command: Callable
    export_selection: bool
    justify: Justify
    show: str
    width: int
    padding: Padding
    format: str
