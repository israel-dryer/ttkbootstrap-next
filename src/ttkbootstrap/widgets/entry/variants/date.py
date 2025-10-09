from typing import Unpack

from ttkbootstrap.widgets import Button
from ttkbootstrap.widgets.entry.shared.entry_field import EntryField
from ttkbootstrap.widgets.entry.types import EntryFieldOptions


class DateEntry(EntryField):
    """A date input field with an optional calendar picker button.

    This widget extends `EntryField` by appending a calendar icon button that can
    be used to trigger a date picker (integration to be implemented externally).
    The calendar button can be shown or hidden dynamically.

    Use the `display_format` option to set the date format:
        - longDate
        - shortDate
        - monthAndDate
        - monthAndYear
        - quarterAndYear
        - day
        - dayOfWeek
        - month
        - quarter
        - year
        - longTime
        - shortTime
        - longDateLongTime
        - shortDateShortTime
        - ... a custom format
    """

    def __init__(
            self, value="", label="", message="", show_picker_button=True, **kwargs: Unpack[EntryFieldOptions]):
        """Initialize a DateEntry widget

        Args:
            value: The initial date value as a string.
            label: Optional label text above the input field.
            message: Optional helper or validation message below the input.
            show_picker_button: Whether to show the calendar icon button.

        Keyword Args:
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
        self._date_picker_button_visible = show_picker_button
        super().__init__(value=value, label=label, message=message, **kwargs)

        self.insert_addon(Button, name='date-picker', icon="calendar-week", take_focus=False)
        self.show_picker_button(show_picker_button)

    @property
    def _date_picker_button(self):
        return self.addons.get('date-picker')

    def show_picker_button(self, value: bool):
        """Show or hide the calendar picker icon button."""
        addon = self.addons.get('date-picker')
        if value:
            addon.attach()
        else:
            addon.hide()

    def _show_date_picker(self):
        # TODO implement date picker dialog
        pass
