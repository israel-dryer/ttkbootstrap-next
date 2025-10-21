from __future__ import annotations

from tkinter import StringVar, ttk
from tkinter.font import Font
from typing import Callable, Literal, TypedDict, Union

from ttkbootstrap.localization.intl_format import FormatSpec
from ttkbootstrap.types import CoreOptions, EventHandler, Justify, Number, Padding, Primitive

DialogType = Literal[
    'openfilename', 'openfile', 'directory', 'openfilenames', 'openfiles',
    'saveasfile', 'saveasfilename'
]


class EntryOptions(CoreOptions, total=False):
    """Configuration options for an Entry widget.

    Attributes:
        cursor: Mouse cursor when hovering.
        export_selection: Whether selection is exported to the clipboard.
        font: Font used to render text.
        foreground: Text (foreground) color.
        justify: Text alignment within the entry.
        padding: Inner padding around the content.
        show: Mask character to display (e.g., '*').
        take_focus: Whether the widget can receive focus.
        text_variable: Variable bound to the entry text.
        width: Widget width in characters.
        xscroll_command: Callback to connect a horizontal scrollbar.
    """
    cursor: str
    export_selection: bool
    font: str | Font
    foreground: str
    justify: Justify
    padding: Padding
    show: str
    take_focus: bool
    text_variable: StringVar
    width: int
    xscroll_command: Callable
    # Formatting/locale
    locale: str


class EntryFieldOptions(EntryOptions, total=False):
    """Configuration options for an Entry Field widget.

    Attributes:
        allow_blank: If True, empty text commits to `None`
        cursor: Mouse cursor when hovering.
        value_format: Intl format spec for parsing/formatting (date/number, etc.).
        export_selection: Whether selection is exported to the clipboard.
        font: Font used to render text.
        foreground: Text (foreground) color.
        id: str
        initial_focus: If true, this widget will receive focus on display.
        justify: Text alignment within the entry.
        kind: The input type, either "entry" or "manualnumeric".
        label: The label text shown above the input field.
        message: The caption or helper message shown below the input field.
        show_messages: If true (default), space is allocated for validation messages.
        parent: Widget
        padding: Inner padding around the content.
        show: Mask character to display (e.g., '*').
        take_focus: Whether the widget can receive focus.
        text_variable: Variable bound to the entry text.
        value: The initial value of the input field.
        width: Widget width in characters.
        xscroll_command: Callback to connect a horizontal scrollbar.
        locale: Locale tag for Intl formatting (e.g., "en_US", "de_DE").
    """
    allow_blank: bool
    initial_focus: bool
    value_format: FormatSpec
    value: str | int | float
    label: str
    message: str
    show_messages: bool
    required: bool
    kind: Literal['entry', 'manualnumeric']


class TextEntryOptions(EntryOptions, total=False):
    """Additional options for text-based Entry widgets.

    Attributes:
        allow_blank: Whether an empty value is considered valid.
        value_format: Format specification used to render/parse the value.
        required: If True, the field must be non-empty to validate.
    """
    allow_blank: bool
    value_format: FormatSpec
    required: bool


class NumberEntryOptions(EntryOptions, total=False):
    """Additional options for numeric Entry widgets.

    Attributes:
        allow_blank: Whether an empty value is valid; if True, empty text commits to `None`.
        cursor: Mouse cursor when hovering.
        value_format: Intl format spec for parsing/formatting (date/number, etc.).
        export_selection: Whether selection is exported to the clipboard.
        font: Font used to render text.
        foreground: Text (foreground) color.
        increment: Step amount applied when adjusting the value.
        initial_focus: If True, the widget requests focus when shown.
        justify: Text alignment within the entry.
        max_value: Maximum allowed value (inclusive).
        min_value: Minimum allowed value (inclusive).
        padding: Inner padding around the content.
        required: If True, the field must be non-empty to validate.
        show: Mask character to display (e.g., '*').
        take_focus: Whether the widget can receive focus.
        text_variable: Variable bound to the entry text.
        width: Widget width in characters.
        wrap: If True, values exceeding bounds wrap around.
        xscroll_command: Callback to connect a horizontal scrollbar.
    """
    allow_blank: bool
    value_format: FormatSpec
    increment: Number
    initial_focus: bool
    label: str
    max_value: Number
    message: str
    min_value: Number
    on_enter: EventHandler
    on_input: EventHandler
    required: bool
    wrap: bool


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
        xscroll_command: A callback used to link the entry to a horizontal scrollbar.
        export_selection: Whether to export the selection to the clipboard (default is True).
        justify: Text justification (left, center, or right).
        show: The character used to mask text (e.g., "*" for passwords).
        width: The width of the entry widget in characters.
    """
    cursor: str
    font: str | Font
    foreground: str
    take_focus: bool
    xscroll_command: Callable
    export_selection: bool
    justify: Justify
    show: str
    width: int
    padding: Padding
    format: str


class SpinboxInputEventData(TypedDict):
    text: str


class SpinboxChangedEventData(TypedDict):
    value: Number
    prev_value: Number
    text: str


class SpinboxEnterEventData(TypedDict):
    value: Number
    text: str


class EntryInputEventData(TypedDict):
    text: str


class EntryChangedEventData(TypedDict):
    value: Primitive
    prev_value: Primitive
    text: str


class EntryEnterEventData(TypedDict):
    value: Primitive
    text: str
