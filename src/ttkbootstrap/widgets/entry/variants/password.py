from typing import Unpack

from ttkbootstrap.events import Event
from ttkbootstrap.widgets import Button
from ttkbootstrap.widgets.entry.shared.entry_field import EntryField
from ttkbootstrap.widgets.entry.types import EntryFieldOptions


class PasswordEntry(EntryField):
    """
    A password input field with optional visibility toggle.

    This widget extends `EntryField` with a bullet-masked entry by default (using "•" for hidden input).
    An optional visibility toggle button can be displayed as a suffix addon. Holding the button
    reveals the password; releasing it hides the input again.
    """

    def __init__(self, value="", label="", message="", show_visible_toggle=False, **kwargs: Unpack[EntryFieldOptions]):
        """Initialize a PasswordEntry widget

        Args:
            value: The initial password value.
            label: Label text displayed above the input.
            message: Optional helper or validation message below the field.
            show_visible_toggle: Whether to show the eye icon to toggle visibility (default is False).

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
            show: Mask character to display (e.g., '•').
            take_focus: Whether the widget can receive focus.
            text_variable: Variable bound to the entry text.
            value: The initial value of the input field.
            width: Widget width in characters.
            x_scroll_command: Callback to connect a horizontal scrollbar.
        """
        self._show_visible_toggle = show_visible_toggle
        self._show_visible_pack = {}

        super().__init__(value=value, label=label, message=message, show="•", **kwargs)

        self.insert_addon(Button, name="visibility", icon="eye", compound="image")
        self.show_visible_toggle(show_visible_toggle)

        addon = self.addons.get('visibility')
        addon.on(Event.CLICK1_DOWN).listen(self._show_password)
        addon.on(Event.CLICK1_UP).listen(self._hide_password)

    @property
    def _visibility_addon(self):
        """Return the visibility toggle IconButton widget."""
        return self.addons.get('visibility')

    def _show_password(self, _):
        """Temporarily reveal the password when the eye icon is pressed."""
        if 'disabled' in self.entry_widget.state():
            return
        self._visibility_addon.configure(icon='eye-slash')
        self.entry_widget.configure(show="")

    def _hide_password(self, _):
        """Hide the password when the eye icon is released."""
        if 'disabled' in self.entry_widget.state():
            return
        self._visibility_addon.configure(icon='eye', compound="image")
        self.entry_widget.configure(show="•")

    def show_visible_toggle(self, value: bool):
        """Show or hide the visibility toggle addon."""
        if value:
            self._visibility_addon.attach()
        else:
            self._visibility_addon.hide()
        return self
