from typing import Any


class IconMixin:
    _style_builder: Any
    _icon: str
    is_disabled: Any
    configure: Any
    has_focus: Any
    bind: Any

    def __init__(self):
        self._selected_state_icon = False
        self._stateful_icons_bound = False
        self._update_icon_assets()

    def _update_icon_assets(self):
        if not self._icon: return
        self._style_builder.build_icon_assets(self._icon)
        if not self._stateful_icons_bound:
            self._bind_stateful_icons()
        if self._is_icon_disabled():
            self._toggle_disable_icon(self.is_disabled())

    def _bind_stateful_icons(self):
        if self._stateful_icons_bound:
            return
        icons = self._style_builder.stateful_icons
        self.configure(image=icons['normal'])

        def on_enter(_):
            if self._is_icon_disabled() or self._selected_state_icon: return
            if self._selected_state_icon: return
            self.configure(image=icons['hover'])

        def on_leave(_):
            if self._is_icon_disabled() or self._selected_state_icon:
                return
            elif self.has_focus():
                self.configure(image=icons['focus'])
            else:
                self.configure(image=icons['normal'])

        def on_press(_):
            if self._is_icon_disabled():
                self.configure(image=icons['pressed'])

        def on_focus_in(_):
            if self._is_icon_disabled():
                self.configure(image=icons['focus'])

        def on_focus_out(_):
            if self._is_icon_disabled(): return
            self.configure(image=icons['normal'])

        def on_selected(_):
            self._selected_state_icon = True
            if 'selected' in icons:
                self.configure(image=icons['selected'])

        def on_deselected(_):
            self._selected_state_icon = False
            self.configure(image=icons['normal'])

        self.bind('enter', on_enter)
        self.bind('leave', on_leave)
        self.bind('focus', on_focus_in)
        self.bind('blur', on_focus_out)
        self.bind('mouse_down', on_press)
        self.bind('selected', on_selected)
        self.bind('deselected', on_deselected)

        self._stateful_icons_bound = True

        # set disabled state
        if self._is_icon_disabled():
            self.configure(image=icons['disabled'])

    def _toggle_disable_icon(self, disable=True):
        icons = self._style_builder.stateful_icons
        if disable:
            self.configure(image=icons['disabled'])
        else:
            self.configure(image=icons['normal'])

    def _is_icon_disabled(self):
        if hasattr(self, 'is_disabled'):
            return self.is_disabled()
        return False