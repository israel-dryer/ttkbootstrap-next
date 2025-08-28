from typing import Unpack

from ttkbootstrap.common.types import Event
from ttkbootstrap.widgets.composites.entry_field import EntryField
from ttkbootstrap.widgets.button import Button
from ttkbootstrap.widgets.parts.entry_part import EntryOptions


class PasswordEntry(EntryField):
    """
    A password input field with optional visibility toggle.

    This widget extends `EntryField` with a bullet-masked entry by default (using "•" for hidden input).
    An optional visibility toggle button can be displayed as a suffix addon. Holding the button
    reveals the password; releasing it hides the input again.

    Parameters:
        value: The initial password value.
        label: Label text displayed above the input.
        message: Optional helper or validation message below the field.
        show_visible_toggle: Whether to show the eye icon to toggle visibility (default is False).
        **kwargs: Additional keyword arguments passed to the EntryPart.
    """

    def __init__(self, value="", label="", message="", show_visible_toggle=False, **kwargs: Unpack[EntryOptions]):
        self._show_visible_toggle = show_visible_toggle
        self._show_visible_pack = {}

        super().__init__(value, label, message, show="•", **kwargs)

        self.insert_addon(Button, name="visibility", icon="eye", compound="image")
        self.show_visible_toggle(show_visible_toggle)

        addon = self.addons.get('visibility')
        addon.bind(Event.MOUSE_DOWN, self._show_password)
        addon.bind(Event.MOUSE_UP, self._hide_password)

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
