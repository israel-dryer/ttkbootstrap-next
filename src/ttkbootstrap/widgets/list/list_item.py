from typing import Optional, TYPE_CHECKING, Unpack

from ttkbootstrap.events import Event
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets.badge import Badge
from ttkbootstrap.widgets.label import Label
from ttkbootstrap.widgets.list.types import ListItemOptions

if TYPE_CHECKING:
    from ttkbootstrap.widgets.button import Button


class ListItem(Pack):

    def __init__(self, **kwargs: Unpack[ListItemOptions]):

        # properties
        self._data = {}
        self._dragging_enabled = kwargs.get('dragging_enabled', False)
        self._deleting_enabled = kwargs.get('deleting_enabled', False)
        self._chevron_visible = kwargs.get('chevron_visible', False)
        self._selection_background = kwargs.get('selection_background', 'primary')
        self._selection_mode = kwargs.get('selection_mode', 'none')
        self._selection_controls_visible = kwargs.get('selection_controls_visible', False)
        self._ignore_selection_by_click = False
        if self._selection_mode != 'none':
            self._ignore_selection_by_click = False if not self._selection_controls_visible else not kwargs.get(
                'select_by_click', False)
        self._set_selection_icon()

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
        self._delete_widget: Optional[Button] = None
        self._badge_widget: Optional[Badge] = None
        self._chevron_widget: Optional[Label] = None
        self._drag_widget: Optional[Button] = None

        self._composite_widgets = set()
        for widget in [self, self._frame_start, self._frame_end, self._frame_center]:
            self._add_composite_widget(widget, ignore_click=self._ignore_selection_by_click)

        # row-level pointer events
        self.on(Event.ENTER).listen(self._on_enter)
        self.on(Event.LEAVE).listen(self._on_leave)

    # Configuration provided through the updater methods

    @property
    def selected(self):
        return self.data.get('selected')

    def _set_selection_icon(self):
        if self._selection_mode == "multiple":
            self._selection_icon = {"name": "square", "state": {"selected": "check-square-fill"}}
        elif self._selection_mode == "single":
            self._selection_icon = {"name": "circle", "state": {"selected": "check-circle-fill"}}
        else:
            self._selection_icon = None

    # ---- event handlers ----

    def _on_enter(self, _):
        # also mark the row container for consistency
        try:
            self.state(['hover'])
        except Exception:
            pass
        for widget in self._composite_widgets:
            try:
                widget.state(['hover'])
            except Exception:
                pass

    def _on_leave(self, event):
        # robust containment check: if moving to a descendant, ignore leave
        related = getattr(event, 'related', None)
        try:
            if related is not None and str(related).startswith(str(self)):
                return "break"
        except Exception:
            pass

        try:
            self.state(['!hover'])
        except Exception:
            pass
        for widget in self._composite_widgets:
            try:
                widget.state(['!hover'])
            except Exception:
                pass
        return None

    def _on_mouse_down(self, _):
        self.focus()
        # Let the list handle selection via emitted event
        self.parent.emit(Event.ITEM_CLICK, data=self._data)
        self.select()
        for widget in self._composite_widgets:
            try:
                widget.state(['pressed'])
            except Exception:
                pass

    def _on_mouse_up(self, _event):
        for widget in self._composite_widgets:
            try:
                widget.state(['!pressed'])
            except Exception:
                pass

    # ---- properties ----

    @property
    def data(self):
        return self._data

    def selection_mode(self, value=None):
        if value is None:
            return self._selection_mode
        else:
            if value != self._selection_mode:
                self._selection_mode = value
                self._set_selection_icon()
                if self._selection_widget is not None:
                    try:
                        self._selection_widget.configure(icon=self._selection_icon)
                    except Exception:
                        pass
            return self

    def selection_controls_visible(self, value=None):
        if value is None:
            return self._selection_controls_visible
        else:
            if value != self._selection_controls_visible:
                self._selection_controls_visible = value
                if value:
                    if self._selection_widget is None:
                        self._selection_widget = Label(
                            parent=self._frame_start,
                            icon=self._selection_icon,
                            variant='list',
                            take_focus=False,
                            builder=dict(select_background=self._selection_background),
                        )
                        self._add_composite_widget(self._selection_widget)
                    self._selection_widget.attach(side="left", padx=5)
                else:
                    if self._selection_widget is not None:
                        self._selection_widget.detach()
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

    # ---- selection + data ----

    def select(self):
        """Emit SELECTED/DESELECTED and let VirtualList reconcile selection via DataSource"""
        mode = self.selection_mode()
        if mode == 'none':
            return None

        is_selected = bool(self.selected or False)
        if is_selected:
            self.parent.emit(Event.ITEM_DESELECTING, data=self.data)
            return False
        else:
            self.parent.emit(Event.ITEM_SELECTING, data=self.data)
            return True

    def delete(self):
        """Unpack this widget and notify subscribers to handle delete action."""
        self.parent.emit(Event.ITEM_DELETING, data=self.data)

    def _update_selection(self, selected: bool = False):
        """Apply selection state atomically (styles + icon) with null guards."""
        mode = self.selection_mode()

        if mode == "none":
            # selection disabled: tear down and clear states
            if self._selection_widget is not None:
                try:
                    self._selection_widget.detach()
                except Exception:
                    pass
                self._composite_widgets.discard(self._selection_widget)
                try:
                    self._selection_widget.destroy()
                except Exception:
                    pass
                self._selection_widget = None
            # clear selected state on row + composites
            try:
                self.state(['!selected'])
            except Exception:
                pass
            for w in list(self._composite_widgets):
                try:
                    w.state(['!selected'])
                    w.emit(Event.COMPOSITE_DESELECT)
                except Exception:
                    pass
            # keep a remembered icon so later comparisons are cheap and safe
            if hasattr(self, '_state'):
                self._state['__sel_icon'] = None
                self._state['selected'] = False
            return

        # Ensure state cache exists
        if not hasattr(self, '_state'):
            self._state = {}

        # Ensure the selection control exists (even if not visible)
        if self._selection_widget is None:
            self._selection_widget = Label(
                parent=self._frame_start,
                icon=self._selection_icon,
                variant='list',
                take_focus=False,
                builder=dict(select_background=self._selection_background),
            )
            if self._selection_controls_visible:
                self._selection_widget.attach(side="left", padx=5)
            self._add_composite_widget(self._selection_widget)

        # Apply selected state to the row + all composites (styles co-update)
        try:
            self.state(['selected' if selected else '!selected'])
        except Exception:
            pass
        for w in list(self._composite_widgets):
            try:
                w.state(['selected' if selected else '!selected'])
            except Exception:
                pass
        for w in list(self._composite_widgets):
            try:
                w.emit(Event.COMPOSITE_SELECT if selected else Event.COMPOSITE_DESELECT)
            except Exception:
                pass

        # Remember logical selected flag
        self._state['selected'] = bool(selected)

    def _update_icon(self, icon=None):
        if icon is not None:
            if not self._icon_widget:
                self._icon_widget = Label(
                    parent=self._frame_start,
                    icon=icon,
                    variant='list',
                    take_focus=False,
                    builder=dict(select_background=self._selection_background)
                ).attach(side='left', padx=6)
                self._add_composite_widget(self._icon_widget, ignore_click=self._ignore_selection_by_click)
            else:
                self._icon_widget.configure(icon=icon)
        else:
            if self._icon_widget:
                self._icon_widget.detach()
                self._composite_widgets.discard(self._icon_widget)
                self._icon_widget.destroy()
                self._icon_widget = None
        pass

    def _update_title(self, text=None):
        if text is not None:
            if not self._title_widget:
                self._title_widget = Label(
                    text=text,
                    parent=self._frame_center,
                    font='heading-lg',
                    variant='list',
                    take_focus=False,
                    builder=dict(select_background=self._selection_background)
                ).attach(fill='x', padx=(0, 3))
                self._add_composite_widget(self._title_widget, ignore_click=self._ignore_selection_by_click)
            else:
                self._title_widget.configure(text=text)
        else:
            if self._title_widget:
                self._title_widget.detach()
                self._composite_widgets.discard(self._title_widget)
                self._title_widget.destroy()
                self._title_widget = None

    def _update_text(self, text=None):
        if text is not None:
            if not self._text_widget:
                self._text_widget = Label(
                    parent=self._frame_center,
                    text=text,
                    variant='list',
                    take_focus=False,
                    builder=dict(select_background=self._selection_background)
                ).attach(fill='x', padx=(0, 3))
                self._add_composite_widget(self._text_widget, ignore_click=self._ignore_selection_by_click)
            else:
                self._text_widget.configure(text=text)
        else:
            if self._text_widget:
                self._text_widget.detach()
                self._composite_widgets.discard(self._text_widget)
                self._text_widget.destroy()
                self._text_widget = None

    def _update_caption(self, text=None):
        if text is not None:
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
                ).attach(fill='x', padx=(0, 3))
                self._add_composite_widget(self._caption_widget, ignore_click=self._ignore_selection_by_click)
            else:
                self._caption_widget.configure(text=text)
        else:
            if self._caption_widget:
                self._caption_widget.detach()
                self._composite_widgets.discard(self._caption_widget)
                self._caption_widget.destroy()
                self._caption_widget = None

    def _update_badge(self, text=None):
        if text is not None:
            if not self._badge_widget:
                self._badge_widget = Badge(
                    parent=self._frame_end,
                    text=text,
                    variant='list',
                    builder=dict(select_background=self._selection_background)
                ).attach(side='right', padx=6)
                self._add_composite_widget(self._badge_widget, ignore_click=self._ignore_selection_by_click)
            else:
                self._badge_widget.configure(text=text)
        else:
            if self._badge_widget:
                self._badge_widget.detach()
                self._composite_widgets.discard(self._badge_widget)
                self._badge_widget.destroy()
                self._badge_widget = None

    def _update_chevron(self):
        if self._chevron_visible:
            if not self._chevron_widget:
                from ttkbootstrap.widgets.button import Button
                self._chevron_widget = Button(
                    parent=self._frame_end,
                    icon='chevron-right',
                    variant='list',
                    take_focus=False,
                    builder=dict(select_background=self._selection_background)
                ).attach(side='right', padx=6)
                self._add_composite_widget(self._chevron_widget, ignore_click=self._ignore_selection_by_click)
        else:
            if self._chevron_widget:
                self._chevron_widget.detach()
                self._composite_widgets.discard(self._chevron_widget)
                self._chevron_widget.destroy()
                self._chevron_widget = None

    def _update_delete(self):
        if self._deleting_enabled:
            if not self._delete_widget:
                from ttkbootstrap.widgets.button import Button
                self._delete_widget = Button(
                    parent=self._frame_end,
                    icon='x-lg',
                    variant='list',
                    take_focus=False,
                    builder=dict(select_background=self._selection_background)
                ).attach(side='right', padx=6)
                self._delete_widget.on(Event.CLICK1_DOWN).listen(lambda _: self.delete())
                self._add_composite_widget(self._delete_widget, ignore_click=True)
        else:
            if self._delete_widget:
                self._delete_widget.detach()
                self._composite_widgets.discard(self._delete_widget)
                self._delete_widget.destroy()
                self._delete_widget = None

    def _update_drag(self):
        if self._dragging_enabled:
            if not self._drag_widget:
                from ttkbootstrap.widgets.button import Button
                self._drag_widget = Button(
                    parent=self._frame_end,
                    icon='grip-vertical',
                    variant='list',
                    cursor='double_arrow',
                    take_focus=False,
                    builder=dict(select_background=self._selection_background)
                ).attach(side='right', padx=6)
                self._add_composite_widget(self._drag_widget, ignore_click=True)
        else:
            if self._drag_widget:
                self._drag_widget.detach()
                self._composite_widgets.discard(self._drag_widget)
                self._drag_widget.destroy()
                self._drag_widget = None

    def update_data(self, record: dict | None):
        """Efficiently update row visuals only when values have changed."""
        if record is None:
            self.detach()
            return

        # Initial state cache
        if not hasattr(self, '_state'):
            self._state = {}

        self._data = record

        selected = bool(record.get("selected", False))
        if self._state.get("selected") != selected:
            self._update_selection(selected)
            self._state["selected"] = selected

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

        self.schedule.idle(self._update_chevron)
        self.schedule.idle(self._update_delete)
        self.schedule.idle(self._update_drag)

    def _add_composite_widget(self, widget, *, ignore_click: bool = False):
        self._composite_widgets.add(widget)
        widget.on(Event.ENTER).listen(self._on_enter)
        widget.on(Event.LEAVE).listen(self._on_leave)

        if not ignore_click:
            widget.on(Event.CLICK1_DOWN).listen(self._on_mouse_down)
            widget.on(Event.CLICK1_UP).listen(self._on_mouse_up)

        try:
            current = set(self.state())
        except Exception:
            current = set()
        for s in ('hover', 'pressed', 'selected'):
            if s in current:
                try:
                    widget.state([s])
                except Exception:
                    pass
