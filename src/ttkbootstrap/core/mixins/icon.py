from __future__ import annotations
from typing import Any, Callable
from ttkbootstrap.utils import resolve_options
from ttkbootstrap.events import Event


class IconMixin:
    _style_builder: Any
    _icon: dict | None
    _has_icon: bool
    exists: Callable[[], bool]
    icon_position: Callable[[str], str]
    is_disabled: Callable[[], bool]
    configure: Callable
    process_idle_tasks: Callable
    has_focus: Callable[[], bool]
    bind: Callable
    schedule_after_idle: Callable

    def __init__(self, *args, **kwargs):
        # Preserve any icon set by subclasses (e.g., Button.__init__)
        self._icon = getattr(self, "_icon", None)
        self._has_icon = getattr(self, "_has_icon", False)

        # Side-effect-free flags
        self._selected_state_icon = False
        self._stateful_icons_bound = False
        self._current_icon_image = None

        # Finish cooperative chain first (Binding/Configure/etc. ready)
        super().__init__(*args, **kwargs)

        # Now it's safe to bind + build assets
        self.bind(Event.THEME_CHANGED, self._on_theme_changed)
        self._update_icon_assets()

    def _set_image_if_needed(self, image):
        """Set the image only if it differs from the current."""
        if image is None:
            return
        if self._current_icon_image is not image:
            self._current_icon_image = image
            self.configure(image=image)

    def icon(self, value=None):
        """Get or set the widget icon"""
        if value is None:
            return self._icon

        key_value = resolve_options(value, "name")
        self._has_icon = True
        self.icon_position("auto")

        def apply():
            if not self.exists():
                return

            if self._icon is None or self._icon.get("name") != key_value["name"]:
                self._icon = key_value
                self._current_icon_image = None  # force image reset
                self._update_icon_assets()

            icons = getattr(self._style_builder, "stateful_icons", {}) if hasattr(self, "_style_builder") else {}
            if not icons:
                return

            if self._selected_state_icon and "selected" in icons:
                self._set_image_if_needed(icons["selected"])
            elif self._is_icon_disabled():
                self._set_image_if_needed(icons.get("disabled", icons.get("normal")))
            elif self.has_focus():
                self._set_image_if_needed(icons.get("focus", icons.get("normal")))
            else:
                self._set_image_if_needed(icons.get("normal"))

        self.schedule_after_idle(apply)
        return self

    def _update_icon_assets(self):
        if not self._icon or not hasattr(self, "_style_builder"):
            return
        # Build (or rebuild) images for current theme
        self._style_builder.build_icon_assets(self._icon)

        # Ensure event bindings only once
        if not self._stateful_icons_bound:
            self._bind_stateful_icons()

        # Apply disabled image immediately if needed
        if self._is_icon_disabled():
            self._toggle_disable_icon(self.is_disabled())
        else:
            # Ensure we show something on first build
            icons = getattr(self._style_builder, "stateful_icons", {})
            if icons:
                self._set_image_if_needed(icons.get("normal"))

    def _bind_stateful_icons(self):
        if self._stateful_icons_bound or not hasattr(self, "_style_builder"):
            return

        icons = getattr(self._style_builder, "stateful_icons", {})
        if not icons:
            return

        self._set_image_if_needed(icons.get("normal"))

        def on_enter(_):
            if self._is_icon_disabled() or self._selected_state_icon:
                return
            self._set_image_if_needed(icons.get("hover", icons.get("normal")))

        def on_leave(_):
            if self._is_icon_disabled() or self._selected_state_icon:
                return
            if self.has_focus():
                self._set_image_if_needed(icons.get("focus", icons.get("normal")))
            else:
                self._set_image_if_needed(icons.get("normal"))

        def on_press(_):
            if not self._is_icon_disabled():
                self._set_image_if_needed(icons.get("pressed", icons.get("normal")))

        def on_focus_in(_):
            if not self._is_icon_disabled():
                self._set_image_if_needed(icons.get("focus", icons.get("normal")))

        def on_focus_out(_):
            if not self._is_icon_disabled():
                self._set_image_if_needed(icons.get("normal"))

        def on_selected(_):
            self._selected_state_icon = True
            self._set_image_if_needed(icons.get("selected", icons.get("normal")))

        def on_deselected(_):
            self._selected_state_icon = False
            self._set_image_if_needed(icons.get("normal"))

        self.bind(Event.ENTER, on_enter)
        self.bind(Event.LEAVE, on_leave)
        self.bind(Event.FOCUS, on_focus_in)
        self.bind(Event.BLUR, on_focus_out)
        self.bind(Event.MOUSE_DOWN, on_press)
        self.bind(Event.SELECTED, on_selected)
        self.bind(Event.DESELECTED, on_deselected)

        self._stateful_icons_bound = True

        if self._is_icon_disabled():
            self._set_image_if_needed(icons.get("disabled", icons.get("normal")))

    def _toggle_disable_icon(self, disable=True):
        icons = getattr(self._style_builder, "stateful_icons", {}) if hasattr(self, "_style_builder") else {}
        image = icons.get("disabled") if disable else icons.get("normal")
        self._set_image_if_needed(image)
        self.process_idle_tasks()

    def _is_icon_disabled(self):
        return self.is_disabled() if hasattr(self, "is_disabled") else False

    def _on_theme_changed(self, _=None):
        # If no icon set, nothing to do
        if not getattr(self, "_icon", None) or not getattr(self, "_style_builder", None):
            return

        # Force a rebuild of assets for the new theme
        self._current_icon_image = None
        self._update_icon_assets()

        icons = getattr(self._style_builder, "stateful_icons", {})
        if not icons:
            return

        if self._selected_state_icon and "selected" in icons:
            image = icons.get("selected", icons.get("normal"))
        elif self._is_icon_disabled():
            image = icons.get("disabled", icons.get("normal"))
        elif self.has_focus():
            image = icons.get("focus", icons.get("normal"))
        else:
            image = icons.get("normal")

        self._set_image_if_needed(image)
