from typing import Unpack

from ttkbootstrap.widgets.composites.entry_field import EntryField
from ttkbootstrap.widgets.parts.entry_part import EntryOptions


class TextEntryOptions(EntryOptions, total=False):
    required: bool

class TextEntry(EntryField):
    """
    A basic single-line text input field with optional label and message.

    This widget extends `EntryField` for plain text input without any suffix or prefix addons.
    It is suitable for generic form fields such as name, email, or titles.

    Parameters:
        value: The initial text value.
        label: Optional label text displayed above the input.
        message: Optional helper or validation message below the input.
        **kwargs: Additional keyword arguments passed to the EntryPart.
    """

    def __init__(self, value: str = "", label: str = "", message: str = "", **kwargs: Unpack[TextEntryOptions]):
        super().__init__(value, label, message, **kwargs)
