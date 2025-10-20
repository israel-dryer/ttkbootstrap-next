from typing import Unpack

from ttkbootstrap.widgets.entry.shared.entry_field import EntryField
from ttkbootstrap.widgets.entry.types import EntryFieldOptions


class TextEntry(EntryField):
    """
    A basic single-line text input field with optional label and message.

    This widget extends `EntryField` for plain text input without any suffix or prefix addons.
    It is suitable for generic form fields such as name, email, or titles.
    """

    def __init__(self, value: str = "", label: str = "", message: str = "", **kwargs: Unpack[EntryFieldOptions]):
        """Initialize a TextEntry widget

        Args:
            value: The initial password value.
            label: Label text displayed above the input.
            message: Optional helper or validation message below the field.

        Keyword Args:
            allow_blank: If True, empty text commits to `None`
            cursor: Mouse cursor when hovering.
            value_format: Intl format spec for parsing/formatting (date/number, etc.).
            export_selection: Whether selection is exported to the clipboard.
            font: Font used to render text.
            foreground: Text (foreground) color.
            initial_focus: If true, this widget will receive focus on display.
            justify: Text alignment within the entry.
            kind: The input type, either "entry" or "manualnumeric".
            label: The label text shown above the input field.
            message: The caption or helper message shown below the input field.
            show_messages: If true (default), space is allocated for validation messages.
            padding: Inner padding around the content.
            show: Mask character to display (e.g., '•').
            take_focus: Whether the widget can receive focus.
            text_variable: Variable bound to the entry text.
            value: The initial value of the input field.
            width: Widget width in characters.
            x_scroll_command: Callback to connect a horizontal scrollbar.
        """
        super().__init__(value=value, label=label, message=message, **kwargs)
