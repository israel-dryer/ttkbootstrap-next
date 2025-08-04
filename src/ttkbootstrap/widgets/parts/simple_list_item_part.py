from typing import Optional

from ttkbootstrap.widgets.layout.frame import Frame
from ttkbootstrap.widgets.buttons.icon_button import IconButton
from ttkbootstrap.widgets.display.label import Label

class SimpleListItemPart(Frame):

    def __init__(self, parent=None, **kwargs):

        # properties
        self._data = kwargs.get('data', dict())
        self._chevron_visible = kwargs.get('chevron_visible', False)
        self._selection_background = kwargs.get('selection_background', 'primary')
        self._selection_mode = kwargs.get('selection_mode', 'none')
        self._selection_controls_visible = kwargs.get('selection_controls_visible', False)

        super().__init__(
            parent,
            variant='list',
            take_focus=True,
            padding=(8, 4),
            builder=dict(select_background=self._selection_background))

        # composite widgets (guaranteed to exist upon init)
        self._frame_start = Frame(
            self, variant='list',
            take_focus=False,
            builder=dict(select_background=self._selection_background)
        ).pack(side='left')

        self._frame_center = Frame(
            self,
            variant='list',
            take_focus=False,
           builder=dict(select_background=self._selection_background)
        ).pack(side='left', fill='x', expand=True)

        self._frame_end = Frame(
            self,
            variant='list',
            take_focus=False
        ).pack(side='right')

        self._selection_widget: Optional[Label] = None
        self._icon_widget: Optional[Label] = None
        self._text_widget: Optional[Label] = None
        self._chevron_widget: Optional[Label] = None

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

    # ---- methods ----

    def select(self):
        mode = self.selection_mode()
        if mode == 'none': return None

        if self.data['selected']:
            self.parent.emit('unselect', data=self.data)
            return False
        else:
            self.parent.emit('select', data=self.data)
            return True

    def delete(self):
        """Unpack this widget and notify subscribers to handle delete action"""
        self.parent.emit('delete', data=self.data)
        self.pack_forget()

    def _update_selection(self, selected=False):
        if self.selection_mode() != 'none':
            if not self._selection_widget:
                if self.selection_mode() == 'multiple':
                    icon = 'check-square-fill' if selected else 'square'
                else:
                    icon = 'check-circle-fill' if selected else 'circle'
                self._selection_widget = Label(
                    self._frame_start,
                    icon=icon,
                    variant='list'
                )
                if self._selection_controls_visible:
                    self._selection_widget.pack(side='left', padx=6)
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
            widget.emit('select' if selected else 'unselect')

    def _update_icon(self, icon=None):
        if icon is not None:
            # add icon and widget if not already existing
            if not self._icon_widget:
                self._icon_widget = Label(
                    self._frame_start,
                    icon=icon,
                    variant='list',
                    take_focus=False,
                    builder=dict(select_background=self._selection_background)
                ).pack(side='left', padx=6)
                self._add_composite_widget(self._icon_widget)
            else:
                # update existing icon
                self._icon_widget.icon(icon)
        else:
            # remove the icon widget
            if self._icon_widget:
                self._icon_widget.pack_forget()
                self._composite_widgets.remove(self._icon_widget)
                self._icon_widget.destroy()
                self._icon_widget = None

    def _update_text(self, text=None):
        if text is not None:
            # add text and widget if not already existing
            if not self._text_widget:
                self._text_widget = Label(
                    self._frame_center,
                    text=text,
                    variant='list',
                    take_focus=False,
                    builder=dict(select_background=self._selection_background)
                ).pack(fill='x', padx=(0, 3))
                self._add_composite_widget(self._text_widget)
            else:
                # update existing text
                self._text_widget.text(text)
        else:
            # remove the text widget
            if self._text_widget:
                self._text_widget.pack_forget()
                self._composite_widgets.remove(self._text_widget)
                self._text_widget.destroy()
                self._text_widget = None

    def _update_chevron(self):
        if self._chevron_visible:
            # add widget if not already existing
            if not self._chevron_widget:
                self._chevron_widget = IconButton(
                    self._frame_end,
                    icon='chevron-right',
                    variant='list',
                    take_focus=False,
                    builder=dict(select_background=self._selection_background)
                ).pack(side='right', padx=6)
                self._add_composite_widget(self._chevron_widget)
        else:
            # remove the widget
            if self._chevron_widget:
                self._chevron_widget.pack_forget()
                self._composite_widgets.remove(self._chevron_widget)
                self._chevron_widget.destroy()
                self._chevron_widget = None

    def update_data(self, record: dict | None):
        """Efficiently update row visuals only when values have changed."""
        if record is None:
            self.pack_forget()
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
            "text": self._update_text,
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

        self.schedule_after_idle(self._update_chevron)

    def _add_composite_widget(self, widget):
        self._composite_widgets.add(widget)
        widget.bind('enter', self._on_enter)
        widget.bind('leave', self._on_leave)
        widget.bind('mouse-down', self._on_mouse_down)
        widget.bind('mouse-up', self._on_mouse_up)
