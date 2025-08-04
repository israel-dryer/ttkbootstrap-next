from .base import EntryField

class TextEntry(EntryField):
    """
    A basic single-line text input field with optional label and message.

    This widget extends `EntryField` for plain text input without any suffix or prefix addons.
    It is suitable for generic form fields such as name, email, or titles.

    Parameters:
        parent: The parent widget.
        value (str, optional): The initial text value.
        label (str, optional): Optional label text displayed above the input.
        message (str, optional): Optional helper or validation message below the input.
        **kwargs: Additional keyword arguments passed to the EntryPart.
    """

    def __init__(self, parent=None, value="", label="", message="", **kwargs):
        super().__init__(parent, value, label, message, **kwargs)
