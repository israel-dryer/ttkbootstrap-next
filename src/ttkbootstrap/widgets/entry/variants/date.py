from typing import Unpack

from ttkbootstrap.widgets import Button
from ttkbootstrap.widgets.entry.shared.entry_field import EntryField
from ttkbootstrap.widgets.entry.shared.entry_part import EntryOptions


class DateEntry(EntryField):
    """
    A date input field with an optional calendar picker button.

    This widget extends `EntryField` by appending a calendar icon button that can
    be used to trigger a date picker (integration to be implemented externally).
    The calendar button can be shown or hidden dynamically.

    Parameters:
        parent: The parent widget.
        value (str, optional): The initial date value as a string.
        label (str, optional): Optional label text above the input field.
        message (str, optional): Optional helper or validation message below the input.
        show_date_picker_button (bool, optional): Whether to show the calendar icon button (default is True).
        **kwargs: Additional keyword arguments passed to the EntryPart.
    """

    def __init__(self, value="", label="", message="", show_date_picker_button=True, **kwargs: Unpack[EntryOptions]):
        self._date_picker_button_visible = show_date_picker_button
        super().__init__(value, label, message, **kwargs)

        self.insert_addon(Button, name='date-picker', icon="calendar-week", take_focus=False)
        self.show_date_picker_button(show_date_picker_button)

    @property
    def _date_picker_button(self):
        return self.addons.get('date-picker')

    def show_date_picker_button(self, value: bool):
        """Show or hide the calendar picker icon button."""
        addon = self.addons.get('date-picker')
        if value:
            addon.attach()
        else:
            addon.hide()

    def _show_date_picker(self):
        # TODO implement date picker dialog
        pass
