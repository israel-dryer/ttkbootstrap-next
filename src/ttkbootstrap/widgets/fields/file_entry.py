from typing import Any, Literal, Callable, Union
from .base import EntryField
from ..buttons.button import Button
from tkinter import filedialog

DialogType = Literal[
    'openfilename', 'openfile', 'directory', 'openfilenames', 'openfiles',
    'saveasfile', 'saveasfilename'
]


class FileEntry(EntryField):
    """
    An entry field with a button that opens a file or directory selection dialog.

    This widget extends `EntryField` to allow users to browse files or folders using
    native Tkinter dialogs. The selected path(s) are inserted into the entry field.
    An optional `on_change` callback can be triggered when a new file is selected.

    Args:
        parent: The parent widget.
        value: Initial value shown in the input field. Defaults to "No file chosen".
        label: Text to display on the button. Defaults to "Choose File".
        dialog_type: Type of dialog to display (e.g., 'openfilename', 'directory').
        dialog_options: Additional options passed to the file dialog (e.g., filetypes).
        on_change: Optional callback function called with the selected file path(s) as a string.
        **kwargs: Additional keyword arguments passed to the EntryPart.
    """

    def __init__(
            self,
            parent=None,
            value: str = "No file chosen",
            label: str = "Choose File",
            dialog_type: DialogType = "openfilename",
            dialog_options: dict[str, Any] = None,
            on_change: Callable[[str], Any] = None,
            **kwargs
    ):
        self._dialog_type = dialog_type
        self._dialog_options = dialog_options or {}
        self._dialog_result = None

        super().__init__(parent, value=value, **kwargs)

        self.insert_addon(
            Button,
            name='file-dialog',
            text=label,
            position="left",
            on_click=self._show_file_chooser
        )

        if on_change:
            self.on_change(on_change)

    @property
    def file_dialog_button(self) -> Button:
        """Return the button widget that triggers the file dialog."""
        return self.addons.get('file-dialog')

    @property
    def dialog_result(self) -> Union[str, list[str], None]:
        """Return the raw result returned by the file dialog."""
        return self._dialog_result

    def dialog_type(self, value: DialogType = None) -> Union[DialogType, 'FileEntry']:
        """
        Get or set the type of file dialog.

        Args:
            value: A valid dialog type string. If None, returns the current value.

        Returns:
            The current dialog type or self (for chaining).
        """
        if value is None:
            return self._dialog_type
        self._dialog_type = value
        return self

    def dialog_options(self, value: dict[str, Any] = None) -> Union[dict[str, Any], 'FileEntry']:
        """
        Get or set the options dictionary passed to the file dialog.

        Args:
            value: A dictionary of dialog options (e.g., filetypes, initialdir). If None, returns current value.

        Returns:
            The current dialog options or self (for chaining).
        """
        if value is None:
            return self._dialog_options
        self._dialog_options = value
        return self

    def _show_file_chooser(self):
        """
        Open the configured file or directory dialog and set the selected path(s) in the entry field.

        Raises:
            ValueError: If an invalid `dialog_type` was provided.
        """
        method_name = f"ask{self._dialog_type}"
        dialog_func = getattr(filedialog, method_name, None)

        if dialog_func is None:
            raise ValueError(f"Invalid dialog type: '{self._dialog_type}'")

        result = dialog_func(**self._dialog_options)
        self._dialog_result = result

        if isinstance(result, (tuple, list)):
            result = ", ".join(result)

        if result:
            self.value(result)
