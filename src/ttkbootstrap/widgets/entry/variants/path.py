from tkinter import filedialog
from typing import Any, Self, Union, Unpack

from ttkbootstrap.events import Event
from ttkbootstrap.widgets import Button
from ttkbootstrap.widgets.entry.shared.entry_field import EntryField
from ttkbootstrap.widgets.entry.shared.entry_part import EntryOptions
from ttkbootstrap.widgets.entry.types import DialogType


class PathEntry(EntryField):
    """
    An entry field with a button that opens a file or directory selection dialog.

    This widget extends `EntryField` to allow users to browse files or folders using
    native Tkinter dialogs. The selected path(s) are inserted into the entry field.
    """

    def __init__(
            self,
            value: str = "No file chosen",
            label: str = "Choose File",
            dialog_type: DialogType = "openfilename",
            dialog_options: dict[str, Any] = None,
            **kwargs: Unpack[EntryOptions]
    ):
        """Initialize a PathEntry widget

        Args:
            value: Initial value shown in the input field. Defaults to "No file chosen".
            label: Text to display on the button. Defaults to "Choose File".
            dialog_type: Type of dialog to display (e.g., 'openfilename', 'directory').
            dialog_options: Additional options passed to the file dialog (e.g., filetypes).

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
            padding: Inner padding around the content.
            show: Mask character to display (e.g., '•').
            take_focus: Whether the widget can receive focus.
            text_variable: Variable bound to the entry text.
            value: The initial value of the input field.
            width: Widget width in characters.
            xscroll_command: Callback to connect a horizontal scrollbar.
        """
        self._dialog_type = dialog_type
        self._dialog_options = dialog_options or {}
        self._dialog_result = None

        super().__init__(value=value, **kwargs)

        self.insert_addon(
            Button,
            name='file-dialog',
            text=label,
            position="left",
            command=self._show_file_chooser
        )

    @property
    def file_dialog_button(self) -> Button:
        """Return the button widget that triggers the file dialog."""
        return self.addons.get('file-dialog')

    @property
    def dialog_result(self) -> Union[str, list[str], None]:
        """Return the raw result returned by the file dialog."""
        return self._dialog_result

    def dialog_type(self, value: DialogType = None) -> Union[DialogType, Self]:
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

    def dialog_options(self, value: dict[str, Any] = None) -> Union[dict[str, Any], Self]:
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
            self.entry_widget.emit(
                Event.CHANGED, value=result, prev_value=self.entry_widget._prev_changed_value, when="tail")
            # prevent event from firing again on blur
            self.entry_widget.commit()
