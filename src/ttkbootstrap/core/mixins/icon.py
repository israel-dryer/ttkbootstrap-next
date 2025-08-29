from typing import Any, Callable
from ttkbootstrap.utils import resolve_options
from ttkbootstrap.events import Event


class IconMixin:
    _style_builder: Any
    _icon: dict | str
    _has_icon: bool
    exists: Callable[[], bool]
    icon_position: Callable[[str], str]
    is_disabled: Callable[[], bool]
    configure: Callable
    process_idle_tasks: Callable
    has_focus: Callable[[], bool]
    bind: Callable

    def __init__(self):
        self._selected_state_icon = False
        self._stateful_icons_bound = False
        self._current_icon_image = None
        self._has_icon = False
        self._update_icon_assets()
        self.bind(Event.THEME_CHANGED, self._on_theme_changed)

    def _set_image_if_needed(self, image):
        """Set the image only if it differs from the current."""
        if self._current_icon_image != image:
            self._current_icon_image = image
            self.configure(image=image)

    def icon(self, value=None):
        """Get or set the widget icon"""
        if value is None:
            return self._icon

        key_value = resolve_options(value, 'name')
        self._has_icon = True
        self.icon_position("auto")

        def apply():
            if not self.exists():
                return

            if self._icon is None or self._icon.get('name', None) != key_value['name']:
                self._icon = key_value
                self._current_icon_image = None  # force image reset
                self._update_icon_assets()

            # Re-apply current state image
            icons = self._style_builder.stateful_icons
            if self._selected_state_icon and 'selected' in icons:
                self._set_image_if_needed(icons['selected'])
            elif self._is_icon_disabled():
                self._set_image_if_needed(icons['disabled'])
            elif self.has_focus():
                self._set_image_if_needed(icons['focus'])
            else:
                self._set_image_if_needed(icons['normal'])

        self.schedule_after_idle(apply)
        return self

    def _update_icon_assets(self):
        if not self._icon:
            return
        self._style_builder.build_icon_assets(self._icon)
        if not self._stateful_icons_bound:
            self._bind_stateful_icons()
        if self._is_icon_disabled():
            self._toggle_disable_icon(self.is_disabled())

    def _bind_stateful_icons(self):
        if self._stateful_icons_bound:
            return
        icons = self._style_builder.stateful_icons
        self._set_image_if_needed(icons['normal'])

        def on_enter(_):
            if self._is_icon_disabled() or self._selected_state_icon:
                return
            self._set_image_if_needed(icons.get('hover', icons['normal']))

        def on_leave(_):
            if self._is_icon_disabled() or self._selected_state_icon:
                return
            if self.has_focus():
                self._set_image_if_needed(icons.get('focus', icons['normal']))
            else:
                self._set_image_if_needed(icons['normal'])

        def on_press(_):
            if not self._is_icon_disabled() and 'pressed' in icons:
                self._set_image_if_needed(icons['pressed'])

        def on_focus_in(_):
            if not self._is_icon_disabled():
                self._set_image_if_needed(icons.get('focus', icons['normal']))

        def on_focus_out(_):
            if not self._is_icon_disabled():
                self._set_image_if_needed(icons['normal'])

        def on_selected(_):
            self._selected_state_icon = True
            self._set_image_if_needed(icons.get('selected', icons['normal']))

        def on_deselected(_):
            self._selected_state_icon = False
            self._set_image_if_needed(icons['normal'])

        self.bind(Event.ENTER, on_enter)
        self.bind(Event.LEAVE, on_leave)
        self.bind(Event.FOCUS, on_focus_in)
        self.bind(Event.BLUR, on_focus_out)
        self.bind(Event.MOUSE_DOWN, on_press)
        self.bind(Event.SELECTED, on_selected)
        self.bind(Event.DESELECTED, on_deselected)

        self._stateful_icons_bound = True

        if self._is_icon_disabled():
            self._set_image_if_needed(icons['disabled'])

    def _toggle_disable_icon(self, disable=True):
        icons = self._style_builder.stateful_icons
        image = icons['disabled'] if disable else icons['normal']
        self._set_image_if_needed(image)
        self.process_idle_tasks()

    def _is_icon_disabled(self):
        if hasattr(self, 'is_disabled'):
            return self.is_disabled()
        return False

    def _on_theme_changed(self, _=None):
        # If no icon set, nothing to do
        if not getattr(self, "_icon", None):
            return

        # Force a rebuild of assets for the new theme
        self._current_icon_image = None
        self._update_icon_assets()

        # Re-apply the correct state image immediately
        icons = self._style_builder.stateful_icons
        if self._selected_state_icon and 'selected' in icons:
            image = icons.get('selected', icons['normal'])
        elif self._is_icon_disabled():
            image = icons.get('disabled', icons['normal'])
        elif self.has_focus():
            image = icons.get('focus', icons['normal'])
        else:
            image = icons['normal']

        # Set unconditionally after cache-bust to ensure redraw
        self._set_image_if_needed(image)
