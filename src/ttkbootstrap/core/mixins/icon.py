from typing import Any


class IconMixin:
    _style_builder: Any
    _icon: str
    is_disabled: Any
    configure: Any
    process_idle_tasks: Any
    has_focus: Any
    bind: Any

    def __init__(self):
        self._selected_state_icon = False
        self._stateful_icons_bound = False
        self._current_icon_image = None
        self._update_icon_assets()

    def _set_image_if_needed(self, image):
        """Set the image only if it differs from the current."""
        if self._current_icon_image != image:
            self._current_icon_image = image
            self.configure(image=image)

    def icon(self, value=None):
        """Get or set the widget icon"""
        if value is None:
            return self._icon
        if self._icon != value:
            self._icon = value
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

        if hasattr(self, 'icon_position') and hasattr(self, '_icon_position'):
            self.icon_position(self._icon_position)
        self.process_idle_tasks()
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

        self.bind('enter', on_enter)
        self.bind('leave', on_leave)
        self.bind('focus', on_focus_in)
        self.bind('blur', on_focus_out)
        self.bind('mouse-down', on_press)
        self.bind('select', on_selected)
        self.bind('unselect', on_deselected)

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
