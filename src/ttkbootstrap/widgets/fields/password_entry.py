from .base import EntryField
from ..buttons.icon_button import IconButton

class PasswordEntry(EntryField):
    """
    A password input field with optional visibility toggle.

    This widget extends `EntryField` with a bullet-masked entry by default (using "•" for hidden input).
    An optional visibility toggle button can be displayed as a suffix addon. Holding the button
    reveals the password; releasing it hides the input again.

    Parameters:
        parent: The parent widget.
        value: The initial password value.
        label: Label text displayed above the input.
        message: Optional helper or validation message below the field.
        show_visible_toggle: Whether to show the eye icon to toggle visibility (default is False).
        **kwargs: Additional keyword arguments passed to the EntryPart.
    """

    def __init__(self, parent=None, value="", label="", message="", show_visible_toggle=False, **kwargs):
        self._show_visible_toggle = show_visible_toggle
        self._show_visible_pack = {}

        super().__init__(parent, value, label, message, show="•", **kwargs)

        self.insert_addon(IconButton, name="visibility", icon="eye")
        self.show_visible_toggle(show_visible_toggle)

        addon = self.addons.get('visibility')
        addon.bind('mouse-down', self._show_password)
        addon.bind('mouse-up', self._hide_password)

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
        self._visibility_addon.configure(icon='eye')
        self.entry_widget.configure(show="•")

    def show_visible_toggle(self, value: bool):
        """Show or hide the visibility toggle addon."""
        if value:
            self._visibility_addon.pack(**self._show_visible_pack)
        else:
            self._show_visible_pack = self._visibility_addon.pack()
            self._visibility_addon.pack_forget()
