from typing import Optional, Union

from ttkbootstrap.widgets import Badge, CheckButton, Frame, IconButton, Label, RadioButton


class ListItemPart(Frame):

    def __init__(
            self,
            parent,
            *,
            key: str,
            icon: str = None,
            text: str = None,
            title: str = None,
            caption: str = None,
            badge: str = None,
            **kwargs):

        # properties
        self._key = key
        self._icon = icon
        self._text = text
        self._title = title
        self._caption = caption
        self._badge = badge

        # other kwargs
        self._show_chevron = kwargs.pop('show_chevron', False)
        self._select_background = kwargs.pop('select_background', 'primary')
        self._selection = kwargs.pop('selection', dict(mode="none"))
        self._selection.setdefault('group', str(parent))
        self._allow_reordering = kwargs.pop('allow_reordering', False)
        self._allow_deleting = kwargs.pop('allow_deleting', False)
        self._hover_state_enabled = kwargs.pop('hover_state_enabled', True)
        self._select_by_click = kwargs.pop('select_by_click', True)
        self._show_selection_control = kwargs.pop('show_selection_control', False)

        # widget state
        self._selected = False

        super().__init__(parent, variant='list', take_focus=True, padding=(8, 4), builder=dict(select_background=self._select_background))

        # composite widgets (guaranteed to exist upon init)
        self._frame_start = Frame(self, variant='list', take_focus=False, builder=dict(select_background=self._select_background)).pack(side='left')
        self._frame_center = Frame(self, variant='list', take_focus=False, builder=dict(select_background=self._select_background)).pack(side='left', fill='x', expand=True)
        self._frame_end = Frame(self, variant='list', take_focus=False, builder=dict(select_background=self._select_background)).pack(side='right')

        self._selection_widget: Optional[Union[CheckButton, RadioButton]] = None
        self._icon_widget: Optional[Label] = None
        self._title_widget: Optional[Label] = None
        self._text_widget: Optional[Label] = None
        self._caption_widget: Optional[Label] = None
        self._delete_widget: Optional[IconButton] = None
        self._badge_widget: Optional[Badge] = None
        self._chevron_widget: Optional[Label] = None
        self._drag_widget: Optional[IconButton] = None

        self._composite_widgets = [self, self._frame_start, self._frame_center, self._frame_end]

        self._build_widget()

        for widget in self._composite_widgets:
            widget.bind('enter', self._on_enter)
            widget.bind('leave', self._on_leave)
            widget.bind('mouse_down', self._on_mouse_down)
            widget.bind('mouse_up', self._on_mouse_up)

        self._selection_widget.on_change(self._on_value_changed)

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

    def _on_value_changed(self, event):
        if self.selection_mode() == 'single':
            self._selected = self._selection_widget.is_selected()
        else:
            self._selected = self._selection_widget.is_checked()

        if self.is_selected:
            for widget in self._composite_widgets:
                widget.state(['selected'])

            self._icon_widget.emit('selected')
            self._chevron_widget.emit('selected')
            self._delete_widget.emit('selected')
            self._drag_widget.emit('selected')
        else:
            self.state(['!selected'])
            for widget in self._composite_widgets:
                widget.state(['!selected'])
            self._icon_widget.emit('deselected')
            self._chevron_widget.emit('deselected')
            self._delete_widget.emit('deselected')
            self._drag_widget.emit('deselected')


    # ---- properties ----

    @property
    def key(self):
        return self._key

    @property
    def data(self):
        return dict(
            key=self._key,
            icon=self._icon,
            text=self._text,
            title=self._title,
            caption=self._caption,
            badge=self._badge
        )

    @property
    def is_selected(self):
        return self._selected

    def title(self, value=None):
        if value is None:
            return self._title
        else:
            self._title = value
            return self

    def text(self, value=None):
        if value is None:
            return self._text
        else:
            self._text = value
            return self

    def caption(self, value=None):
        if value is None:
            return self._caption
        else:
            self._caption = value
            return self

    def badge(self, value=None):
        if value is None:
            return self._badge
        else:
            self._badge = value
            return self

    def icon(self, value=None):
        if value is None:
            return self._icon
        else:
            self._icon = value
            return self

    def selection_mode(self, value=None):
        if value is None:
            return self._selection['mode']
        else:
            self._selection.update(mode=value)
            return self

    def selection_color(self, value=None):
        if value is None:
            return self._selection['color']
        else:
            self._selection.update(color=value)
            return self

    def selection_group(self, value=None):
        if value is None:
            return self._selection['group']
        else:
            self._selection.update(group=value)
            return self

    def show_chevron(self, value=None):
        if value is None:
            return self._show_chevron
        else:
            self._show_chevron = value
            return self

    def allow_reordering(self, value=None):
        if value is None:
            return self._allow_reordering
        else:
            self._allow_reordering = value
            return self

    def allow_deleting(self, value=None):
        if value is None:
            return self._allow_deleting
        else:
            self._allow_deleting = value
            return self

    def hover_state_enabled(self, value=None):
        if value is None:
            return self._hover_state_enabled
        else:
            self._hover_state_enabled = value
            return self

    # ---- methods ----

    def select(self):
        mode = self.selection_mode()
        if mode == 'none': return False

        # checkbox widget
        if mode == 'single':
            self._selection_widget.select()
            self._selected = self._selection_widget.is_selected()
        else:
            # checkbutton widget
            self._selection_widget.toggle()
            self._selected = self._selection_widget.is_checked()

        if self._selected:
            self.parent.emit('selected', data=self.data)
        else:
            self.parent.emit('deselected', data=self.data)
        return self._selected

    def delete(self):
        """Unpack this widget and notify subscribers to handle delete action"""
        self.parent.emit('deleted', data=self.data)
        self.pack_forget()

    def _build_widget(self):
        self._build_selection()
        self._build_icon()
        self._build_title()
        self._build_text()
        self._build_caption()
        self._build_drag()
        self._build_chevron()
        self._build_delete()
        self._build_badge()

    def _build_selection(self):
        if self.selection_mode() == 'multiple':
            self._selection_widget = CheckButton(self._frame_start)
        else:
            self._selection_widget = RadioButton(
                self._frame_start,
                value=self.key,
                group=self.selection_group(),
                color=self.selection_color(),
                variant='list',
                take_focus=False,
            )
        # if self.selection_mode() == 'none': return
        # if self._selection_widget and self._show_selection_control:
        #     self._selection_widget.pack(side='left')

    def _build_icon(self):
        self._icon_widget = Label(
            self._frame_start,
            icon=self.icon() or 'patch-fill',
            variant='list',
            take_focus=False,
            builder=dict(select_background=self._select_background)
        )
        if self.icon():
            self._composite_widgets.append(self._icon_widget)
            self._icon_widget.pack(side='left', padx=6)

    def _build_title(self):
        self._title_widget = Label(
            self._frame_center,
            text=self.title() or '',
            font='heading-lg',
            variant='list',
            take_focus=False,
            builder=dict(select_background=self._select_background)
        )
        if self.title():
            self._composite_widgets.append(self._title_widget)
            self._title_widget.pack(fill='x', padx=(0, 3))

    def _build_text(self):
        self._text_widget = Label(
            self._frame_center,
            text=self.text() or '',
            variant='list',
            take_focus=False,
            builder=dict(select_background=self._select_background)
        )
        if self.text():
            self._composite_widgets.append(self._text_widget)
            self._text_widget.pack(fill='x', padx=(0, 3))

    def _build_caption(self):
        self._caption_widget = Label(
            self._frame_center,
            text=self.caption() or '',
            font='caption',
            anchor='w',
            foreground='secondary',
            variant='list',
            take_focus=False,
            builder=dict(select_background=self._select_background)
        )
        if self.caption():
            self._composite_widgets.append(self._caption_widget)
            self._caption_widget.pack(fill='x', padx=(0, 3))

    def _build_badge(self):
        self._badge_widget = Badge(
            self._frame_end,
            text=self.badge() or '',
            variant='list',
            builder=dict(select_background=self._select_background)
        )
        if self.badge():
            self._composite_widgets.append(self._badge_widget)
            self._badge_widget.pack(side='right', padx=6)

    def _build_chevron(self):
        self._chevron_widget = IconButton(
            self._frame_end,
            icon='chevron-right',
            variant='list',
            take_focus=False,
            builder=dict(select_background=self._select_background)
        )
        if self.show_chevron():
            self._composite_widgets.append(self._chevron_widget)
            self._chevron_widget.pack(side='right', padx=6)

    def _build_delete(self):
        self._delete_widget = IconButton(
            self._frame_end,
            icon='x-lg',
            variant='list',
            take_focus=False,
            builder=dict(select_background=self._select_background)
        )
        self._delete_widget.bind('mouse_down', lambda _:self.delete())

        if self.allow_deleting():
            self._composite_widgets.append(self._delete_widget)
            self._delete_widget.pack(side='right', padx=6)

    def _build_drag(self):
        self._drag_widget = IconButton(
            self._frame_end,
            icon='grip-vertical',
            variant='list',
            cursor='double_arrow',
            take_focus=False,
            builder=dict(select_background=self._select_background)
        )
        if self.allow_reordering():
            self._composite_widgets.append(self._drag_widget)
            self._drag_widget.pack(side='right', padx=6)
