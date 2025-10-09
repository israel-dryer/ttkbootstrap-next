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
        x_scroll_command: Callback to connect a horizontal scrollbar.
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
    x_scroll_command: Callable


class EntryFieldOptions(EntryOptions, total=False):
    """Configuration options for an Entry Field widget.

    Attributes:
        allow_blank: If True, empty text commits to `None`
        cursor: Mouse cursor when hovering.
        display_format: Intl format spec for parsing/formatting (date/number, etc.).
        export_selection: Whether selection is exported to the clipboard.
        font: Font used to render text.
        foreground: Text (foreground) color.
        initial_focus: If true, this widget will receive focus on display.
        justify: Text alignment within the entry.
        kind: The input type, either "entry" or "spinbox".
        label: The label text shown above the input field.
        message: The caption or helper message shown below the input field.
        padding: Inner padding around the content.
        show: Mask character to display (e.g., '*').
        take_focus: Whether the widget can receive focus.
        text_variable: Variable bound to the entry text.
        value: The initial value of the input field.
        width: Widget width in characters.
        x_scroll_command: Callback to connect a horizontal scrollbar.
    """
    allow_blank: bool
    initial_focus: bool
    display_format: FormatSpec
    value: str | int | float
    label: str
    message: str
    required: bool
    kind: Literal['entry', 'spinbox']


class TextEntryOptions(EntryOptions, total=False):
    """Additional options for text-based Entry widgets.

    Attributes:
        allow_blank: Whether an empty value is considered valid.
        display_format: Format specification used to render/parse the value.
        required: If True, the field must be non-empty to validate.
    """
    allow_blank: bool
    display_format: FormatSpec
    required: bool


class NumberEntryOptions(EntryOptions, total=False):
    """Additional options for numeric Entry widgets.

    Attributes:
        allow_blank: Whether an empty value is considered valid.
        display_format: Format specification for rendering/parsing numbers.
        increment: Step amount applied when adjusting the value.
        initial_focus: If True, the widget requests focus when created/shown.
        max_value: Maximum allowed value (inclusive).
        min_value: Minimum allowed value (inclusive).
        on_enter: Event handler fired when the user presses Enter/Return.
        on_input: Event handler fired as the user edits the value.
        required: If True, the field must be non-empty to validate.
        wrap: If True, values exceeding bounds wrap around.
    """
    allow_blank: bool
    display_format: FormatSpec
    increment: Number
    initial_focus: bool
    max_value: Number
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
