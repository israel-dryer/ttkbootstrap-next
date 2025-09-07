from typing import Optional, TYPE_CHECKING

from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets.badge import Badge
from ttkbootstrap.widgets.label import Label
from ttkbootstrap.events import Event

if TYPE_CHECKING:
    from ttkbootstrap.widgets.button import Button


class ListItem(Pack):

    def __init__(self, **kwargs):

        # properties
        self._data = kwargs.get('data', dict())
        self._dragging_enabled = kwargs.get('dragging_enabled', False)
        self._deleting_enabled = kwargs.get('deleting_enabled', False)
        self._chevron_visible = kwargs.get('chevron_visible', False)
        self._selection_background = kwargs.get('selection_background', 'primary')
        self._selection_mode = kwargs.get('selection_mode', 'none')
        self._selection_controls_visible = kwargs.get('selection_controls_visible', False)

        super().__init__(
            direction="horizontal",
            variant='list',
            take_focus=True,
            padding=(8, 4),
            builder=dict(select_background=self._selection_background),
            parent=kwargs.pop('parent', None))

        # composite widgets (guaranteed to exist upon init)
        self._frame_start = Pack(
            direction="horizontal",
            parent=self,
            variant='list',
            take_focus=False,
            builder=dict(select_background=self._selection_background)
        ).attach()

        self._frame_center = Pack(
            parent=self,
            variant='list',
            take_focus=False,
            builder=dict(select_background=self._selection_background)
        ).attach(fill='x', expand=True)

        self._frame_end = Pack(
            parent=self,
            variant='list',
            take_focus=False,
            builder=dict(select_background=self._selection_background)
        ).attach()

        self._selection_widget: Optional[Label] = None
        self._icon_widget: Optional[Label] = None
        self._title_widget: Optional[Label] = None
        self._text_widget: Optional[Label] = None
        self._caption_widget: Optional[Label] = None
        self._delete_widget: Optional["Button"] = None
        self._badge_widget: Optional[Badge] = None
        self._chevron_widget: Optional[Label] = None
        self._drag_widget: Optional["Button"] = None

        self._composite_widgets = set()
        for widget in [self, self._frame_start, self._frame_end, self._frame_center]:
            self._add_composite_widget(widget)

    # ---- event handlers ----

    def _on_enter(self, _):
        for widget in self._composite_widgets:
            widget.state(['hover'])

    def _on_leave(self, event):
        if event.widget != str(self):
            self._on_enter(None)
            return "break"
        for widget in self._composite_widgets:
            widget.state(['!hover'])
        return None

    def _on_mouse_down(self, _):
        self.focus()
        self.select()
        for widget in self._composite_widgets:
            widget.state(['pressed'])

    def _on_mouse_up(self, event):
        for widget in self._composite_widgets:
            widget.state(['!pressed'])

    # ---- properties ----

    @property
    def data(self):
        return self._data

    def selection_mode(self, value=None):
        if value is None:
            return self._selection_mode
        else:
            self._selection_mode = value
            return self

    def selection_controls_visible(self, value=None):
        if value is None:
            return self._selection_controls_visible
        else:
            self._selection_controls_visible = value
            return self

    def selection_background(self, value=None):
        if value is None:
            return self._selection_background
        else:
            self._selection_background = value
            return self

    def chevron_visible(self, value=None):
        if value is None:
            return self._chevron_visible
        else:
            self._chevron_visible = value
            return self

    def dragging_enabled(self, value=None):
        if value is None:
            return self._dragging_enabled
        else:
            self._dragging_enabled = value
            return self

    def deleting_enabled(self, value=None):
        if value is None:
            return self._deleting_enabled
        else:
            self._deleting_enabled = value
            return self

    # ---- methods ----

    def select(self):
        mode = self.selection_mode()
        if mode == 'none': return None

        if self.data['selected']:
            self.parent.emit(Event.DESELECTED, data=self.data)
            return False
        else:
            self.parent.emit(Event.SELECTED, data=self.data)
            return True

    def delete(self):
        """Unpack this widget and notify subscribers to handle delete action"""
        self.parent.emit(Event.DELETE, data=self.data)
        self.detach()

    def _update_selection(self, selected=False):
        if self.selection_mode() != 'none':
            if not self._selection_widget:
                if self.selection_mode() == 'multiple':
                    icon = 'check-square-fill' if selected else 'square'
                else:
                    icon = 'check-circle-fill' if selected else 'circle'
                self._selection_widget = Label(
                    parent=self._frame_start,
                    icon=icon,
                    variant='list'
                )
                if self._selection_controls_visible:
                    self._selection_widget.attach(side="left", marginx=5)
                self._add_composite_widget(self._selection_widget)
            else:
                if self.selection_mode() == 'multiple':
                    self._selection_widget.icon('check-square-fill' if selected else 'square')
                else:
                    self._selection_widget.icon('check-circle-fill' if selected else 'circle')
                for widget in self._composite_widgets:
                    widget.state(['selected' if selected else '!selected'])
        else:
            if self._selection_widget:
                self._selection_widget.destroy()
        for widget in self._composite_widgets:
            widget.emit(Event.SELECTED if selected else Event.DESELECTED)

    def _update_icon(self, icon=None):
        if icon is not None:
            # add icon and widget if not already existing
            if not self._icon_widget:
                self._icon_widget = Label(
                    parent=self._frame_start,
                    icon=icon,
                    variant='list',
                    take_focus=False,
                    builder=dict(select_background=self._selection_background)
                ).attach(side='left', marginx=6)
                self._add_composite_widget(self._icon_widget)
            else:
                # update existing icon
                self._icon_widget.icon(icon)
        else:
            # remove the icon widget
            if self._icon_widget:
                self._icon_widget.detach()
                self._composite_widgets.remove(self._icon_widget)
                self._icon_widget.destroy()
                self._icon_widget = None

    def _update_title(self, text=None):
        if text is not None:
            # add text and widget if not already existing
            if not self._title_widget:
                self._title_widget = Label(
                    text=text,
                    parent=self._frame_center,
                    font='heading-lg',
                    variant='list',
                    take_focus=False,
                    builder=dict(select_background=self._selection_background)
                ).attach(fill='x', marginx=(0, 3))
                self._add_composite_widget(self._title_widget)
            else:
                # update existing title
                self._title_widget.text(text)
        else:
            # remove the title widget
            if self._title_widget:
                self._title_widget.detach()
                self._composite_widgets.remove(self._title_widget)
                self._title_widget.destroy()
                self._title_widget = None

    def _update_text(self, text=None):
        if text is not None:
            # add text and widget if not already existing
            if not self._text_widget:
                self._text_widget = Label(
                    parent=self._frame_center,
                    text=text,
                    variant='list',
                    take_focus=False,
                    builder=dict(select_background=self._selection_background)
                ).attach(fill='x', marginx=(0, 3))
                self._add_composite_widget(self._text_widget)
            else:
                # update existing text
                self._text_widget.text(text)
        else:
            # remove the text widget
            if self._text_widget:
                self._text_widget.detach()
                self._composite_widgets.remove(self._text_widget)
                self._text_widget.destroy()
                self._text_widget = None

    def _update_caption(self, text=None):
        if text is not None:
            # add text and widget if not already existing
            if not self._caption_widget:
                self._caption_widget = Label(
                    parent=self._frame_center,
                    text=text,
                    font='caption',
                    anchor='w',
                    foreground='secondary',
                    variant='list',
                    take_focus=False,
                    builder=dict(select_background=self._selection_background)
                ).attach(fill='x', marginx=(0, 3))
                self._add_composite_widget(self._caption_widget)
            else:
                # update existing text
                self._caption_widget.text(text)
        else:
            # remove the text widget
            if self._caption_widget:
                self._caption_widget.detach()
                self._composite_widgets.remove(self._caption_widget)
                self._caption_widget.destroy()
                self._caption_widget = None

    def _update_badge(self, text=None):
        if text is not None:
            # add text and widget if not already existing
            if not self._badge_widget:
                self._badge_widget = Badge(
                    parent=self._frame_end,
                    text=text,
                    variant='list',
                    builder=dict(select_background=self._selection_background)
                ).attach(side='right', marginx=6)
                self._add_composite_widget(self._badge_widget)
            else:
                # update existing text
                self._badge_widget.text(text)
        else:
            # remove the text widget
            if self._badge_widget:
                self._badge_widget.detach()
                self._composite_widgets.remove(self._badge_widget)
                self._badge_widget.destroy()
                self._badge_widget = None

    def _update_chevron(self):
        if self._chevron_visible:
            # add widget if not already existing
            if not self._chevron_widget:
                from ttkbootstrap.widgets.button import Button
                self._chevron_widget = Button(
                    parent=self._frame_end,
                    icon='chevron-right',
                    variant='list',
                    take_focus=False,
                    builder=dict(select_background=self._selection_background)
                ).attach(side='right', marginx=6)
                self._add_composite_widget(self._chevron_widget)
        else:
            # remove the widget
            if self._chevron_widget:
                self._chevron_widget.detach()
                self._composite_widgets.remove(self._chevron_widget)
                self._chevron_widget.destroy()
                self._chevron_widget = None

    def _update_delete(self):
        if self._deleting_enabled:
            # add widget if not already existing
            if not self._delete_widget:
                from ttkbootstrap.widgets.button import Button
                self._delete_widget = Button(
                    parent=self._frame_end,
                    icon='x-lg',
                    variant='list',
                    take_focus=False,
                    builder=dict(select_background=self._selection_background)
                ).attach(side='right', marginx=6)
                self._delete_widget.on(Event.MOUSE_DOWN).listen(lambda _: self.delete())
                self._add_composite_widget(self._delete_widget)
        else:
            # remove the widget
            if self._delete_widget:
                self._delete_widget.detach()
                self._composite_widgets.remove(self._delete_widget)
                self._delete_widget.destroy()
                self._delete_widget = None

    def _update_drag(self):
        if self._dragging_enabled:
            # add widget if not already existing
            if not self._drag_widget:
                from ttkbootstrap.widgets.button import Button
                self._drag_widget = Button(
                    parent=self._frame_end,
                    icon='grip-vertical',
                    variant='list',
                    cursor='double_arrow',
                    take_focus=False,
                    builder=dict(select_background=self._selection_background)
                ).attach(side='right', marginx=6)
                self._add_composite_widget(self._drag_widget)
        else:
            # remove the widget
            if self._drag_widget:
                self._drag_widget.detach()
                self._composite_widgets.remove(self._drag_widget)
                self._drag_widget.destroy()
                self._drag_widget = None

    def update_data(self, record: dict | None):
        """Efficiently update row visuals only when values have changed."""
        if record is None:
            self.detach()
            return

        # Initial state setup
        if not hasattr(self, '_state'):
            self._state = {}

        self._data = record
        selected = record.get("selected", False)

        # Efficient selection update
        if self._state.get("selected") != selected:
            self._update_selection(selected)

        # Direct update for high-priority visuals
        for field, updater in {
            "title": self._update_title,
            "text": self._update_text,
            "caption": self._update_caption,
            "icon": self._update_icon,
        }.items():
            value = record.get(field)
            if self._state.get(field) != value:
                updater(value)
                self._state[field] = value

        # Defer low-priority visuals
        def defer(field, updater):
            value = record.get(field)
            if self._state.get(field) != value:
                self.schedule_after_idle(lambda: updater(value))
                self._state[field] = value

        defer("badge", self._update_badge)
        self.schedule_after_idle(self._update_chevron)
        self.schedule_after_idle(self._update_delete)
        self.schedule_after_idle(self._update_drag)

    def _add_composite_widget(self, widget):
        widget.update_style()  # for some reason, update_style will not be invoked by theme_change on composite.
        self._composite_widgets.add(widget)
        widget.on(Event.ENTER).listen(self._on_enter)
        widget.on(Event.LEAVE).listen(self._on_leave)
        widget.on(Event.MOUSE_DOWN).listen(self._on_mouse_down)
        widget.on(Event.MOUSE_UP).listen(self._on_mouse_up)
