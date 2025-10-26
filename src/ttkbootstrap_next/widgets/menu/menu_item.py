from typing import Literal, cast

from ttkbootstrap_next import Event
from ttkbootstrap_next.layouts.grid import Grid
from ttkbootstrap_next.widgets.label import Label

type MenuItemType = Literal['button', 'checkbutton', 'radiobutton', 'selectbox', 'cascade']


class MenuItem(Grid):
    def __init__(self, **kwargs):
        self._data = {}
        self._item_index = 0
        self._items = []
        self._selected = kwargs.get('selected', False)
        self._item_type: MenuItemType = kwargs.pop('item_type', cast(MenuItemType, 'button'))
        self._begin_group = kwargs.pop("begin_group", False)
        self._icon = kwargs.pop('icon', "none")
        self._image = kwargs.pop('image', "none")
        self._label = kwargs.pop('label', "")
        self._underline = kwargs.get('underline', None)
        self._command = kwargs.pop('command', None)
        self._accelerator = kwargs.pop('accelerator', None)
        self._command = kwargs.pop('command', None)

        super().__init__(
            columns=["24px", 1, "24px"],
            rows=1,
            gap=8,
            padding=(8, 4),
            take_focus=False,
            variant="menu-item",
            parent=kwargs.pop('parent', None)
        )
        self._style_builder.options(begin_group=self._begin_group)

        # composite widgets
        self._before = Label(parent=self, variant="menu-item").attach(column=0)

        if self._item_type == "radiobutton":
            self._before.configure(icon={"name": "circle", "state": {"selected": "check-circle-fill"}})
        elif self._item_type == "checkbutton":
            self._before.configure(icon={"name": "square", "state": {"selected": "check-square-fill"}})
        elif self._icon:
            self._before.configure(icon=self._icon)

        self._center = Label(self._label, parent=self, font="body", variant="menu-item", anchor="w").attach(
            column=1, sticky="ew")
        if self._underline is not None:
            self._center.configure(underline=self._underline)

        self._after = Label(parent=self, variant="menu-item", anchor="center").attach(column=2, sticky="e")

        if self._accelerator:
            self._after.configure(text=self._accelerator, font="body", foreground="secondary")
        elif self._item_type == 'cascade':
            self._after.configure(icon="chevron-right")

        # row-level pointer events
        self.on(Event.ENTER)
        self.on(Event.LEAVE)
        self.on(Event.FOCUS)
        self.on(Event.BLUR)
        self.on(Event.KEYDOWN_SPACE)

        self._composite_widgets = set()
        for widget in [self, self._before, self._center, self._after]:
            self._add_composite_widget(widget)

    @property
    def data(self):
        return self._data

    @property
    def selected(self):
        return self._selected

    def select(self):
        """Emit SELECTED/DESELECTED and let VirtualList reconcile selection via DataSource"""
        if self._item_type != 'radiobutton' and self._item_type != 'checkbutton':
            print("Bailing out...", self._item_type)
            return

        self._selected = not self._selected
        if self.selected:
            # In single selection mode, don't allow deselecting the selected item
            self._before.state(['selected'])
        else:
            self._before.state(['!selected'])

        print("select", self._selected, "state", self._before.state(), "icon", self._before.configure('icon'))

    def _on_enter(self, _):
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
        # Let the list handle selection via emitted event
        self.parent.emit(Event.ITEM_CLICK, data=self._data)
        self.select()
        for widget in self._composite_widgets:
            try:
                widget.state(['pressed'])
            except Exception:
                pass

    def _on_mouse_up(self, _):
        for widget in self._composite_widgets:
            try:
                widget.state(['!pressed'])
            except Exception:
                pass

    def _add_composite_widget(self, widget):
        self._composite_widgets.add(widget)
        widget.on(Event.ENTER).listen(self._on_enter)
        widget.on(Event.LEAVE).listen(self._on_leave)
        widget.on(Event.CLICK1_DOWN).listen(self._on_mouse_down)
        widget.on(Event.CLICK1_UP).listen(self._on_mouse_up)

        try:
            current = set(self.state())
        except Exception:
            current = set()
        for s in ('hover', 'pressed', 'focus'):
            if s in current:
                try:
                    widget.state([s])
                except Exception:
                    pass
