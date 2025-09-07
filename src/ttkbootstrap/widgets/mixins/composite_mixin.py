class CompositeWidgetMixin:
    """Mixin to synchronize interactive states (hover, pressed, etc.) between a container
    and its internal child widgets, with correct handling of overlapping events."""

    def __init__(self, *args, **kwargs):
        # composite state registry
        self._composite_states = dict(enter=[], leave=[], mouse_down=[], mouse_up=[])
        self._composite_callbacks = dict(
            enter=self._on_enter,
            leave=self._on_leave,
            mouse_down=self._on_mouse_down,
            mouse_up=self._on_mouse_up
        )
        self._hover_count = 0
        super().__init__(*args, **kwargs)

    def _register_composite_states(self, widget, events=None):
        events = events or ['enter', 'leave', 'mouse-down', 'mouse-up']
        for event in events:
            self._composite_states[event].append(widget)
            widget.on(event).listen(self._composite_callbacks[event])

    def _apply_state(self, event: str, state: str, enable: bool):
        for widget in self._composite_states[event]:
            if enable:
                widget.state([state])
            else:
                widget.state([f"!{state}"])

    def _on_enter(self, _):
        self._hover_count += 1
        if self._hover_count == 1:
            self._apply_state('enter', 'hover', True)

    def _on_leave(self, _):
        self._hover_count = max(0, self._hover_count - 1)
        if self._hover_count == 0:
            self._apply_state('leave', 'hover', False)

    def _on_mouse_down(self, _):
        if hasattr(self, 'select') and hasattr(self, 'is_selected'):
            self.select()
            if self.is_selected:
                self._apply_state('mouse-down', 'selected', True)
            else:
                self._apply_state('mouse-down', 'selected', False)

    def _on_mouse_up(self, _):
        pass
