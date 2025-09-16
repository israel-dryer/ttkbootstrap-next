from tkinter import TclError, ttk
from typing import Any, Callable, Literal, Optional, Self, TypedDict, Union, Unpack, cast

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.core.layout_context import pop_container, push_container
from ttkbootstrap.events import Event
from ttkbootstrap.exceptions.base import NavigationError
from ttkbootstrap.interop.runtime.binding import Stream
from ttkbootstrap.layouts import Grid, Pack
from ttkbootstrap.style.builders.notebook import NotebookStyleBuilder
from ttkbootstrap.types import (
    Anchor, Compound, CoreOptions, EventHandler, Fill, Gap, Image, Padding, Sticky, Widget,
)


# ---------- Options ----------

class NotebookOptions(CoreOptions, total=False):
    take_focus: bool
    width: int
    height: int
    padding: Padding


class NotebookTabOptions(TypedDict, total=False):
    text: str
    compound: Compound
    image: Image
    underline: int
    state: Literal['normal', 'disabled', 'hidden']


class GridTabOptions(NotebookTabOptions, total=False):
    rows: Union[int, list[Union[int, str]]]
    columns: Union[int, list[Union[int, str]]]
    gap: Gap
    padding: Padding
    sticky_items: Sticky
    propagate: bool
    auto_flow: Literal['row', 'column', 'dense-row', 'dense-column', 'none']
    surface: str
    variant: str
    parent: Widget


class PackTabOptions(NotebookTabOptions, total=False):
    direction: Literal["horizontal", "vertical", "row", "column", "row-reverse", "column-reverse"]
    gap: int
    padding: Padding
    propagate: bool
    expand_items: bool
    fill_items: Fill
    anchor_items: Anchor
    surface: str
    variant: str
    parent: Widget


# ---------- Tab mixin with KEY (replaces "name") ----------

class TabMixin:
    """Mixin that adds tab metadata and tab-specific options."""
    bind: Callable
    widget: Widget

    def __init__(self, **kwargs):
        # Stable developer key (optional; Notebook will auto-generate if missing)
        self._tab_key: Optional[str] = kwargs.pop('key', None)

        # Keep ttk tab options for .add()
        self._tab_options = {}
        for k in ['underline', 'state', 'sticky', 'image', 'compound', 'text']:
            if k in kwargs:
                self._tab_options[k] = kwargs.pop(k)

        super().__init__(**kwargs)

    @property
    def key(self) -> Optional[str]:
        """Stable developer key for this tab (if provided)."""
        return self._tab_key


class TabGrid(TabMixin, Grid):
    def __init__(self, text: str = "", *, key: str | None = None, **kwargs: Unpack[GridTabOptions]):
        super().__init__(text=text, key=key, **kwargs)
        self._on_activated = None
        self._on_deactivated = None


class TabPack(TabMixin, Pack):
    def __init__(self, text: str = "", *, key: str | None = None, **kwargs: Unpack[PackTabOptions]):
        super().__init__(text=text, key=key, **kwargs)


# A "tab" handle can be key (str), index (int), widget, or tk id string
Tab = Union[str, int, TabGrid, TabPack]


# ---------- Notebook ----------

class Notebook(BaseWidget):
    """Wrapper around ttk.Notebook with stable key-based tab identity."""
    Pack = TabPack
    Grid = TabGrid
    widget: ttk.Notebook

    def __init__(self, **kwargs: Unpack[NotebookOptions]):
        self._in_context: bool = False
        self._style_builder = NotebookStyleBuilder()

        # Key registries
        self._key_registry: dict[str, Widget] = {}  # key -> wrapper widget
        self._tk_to_key: dict[str, str] = {}  # tk id -> key
        self._auto_counter: int = 0  # for auto keys: tab1, tab2, ...

        parent = kwargs.pop('parent', None)
        tk_options = dict(**kwargs)
        super().__init__(ttk.Notebook, tk_options, parent=parent)

        # Change-tracking for enriched events
        self._last_selected: str | None = None
        try:
            self._last_selected = self.widget.select()
        except Exception:
            self._last_selected = None
        self._last_change_reason: Literal['user', 'api', 'hide', 'forget', 'reorder', 'unknown'] = 'unknown'
        self._last_change_via: Literal['click', 'key', 'programmatic', 'unknown'] = 'unknown'

    # ---- context ----
    def __enter__(self):
        push_container(self)
        self._in_context = True
        return self

    def __exit__(self, exc_type, exc, tb):
        pop_container()
        self._in_context = False

    # ---- internal helpers ----
    def _mark_api_change(self, reason: str = 'api'):
        self._last_change_reason = reason
        self._last_change_via = 'programmatic'

    def _make_key(self, widget: Widget, explicit_key: Optional[str]) -> str:
        """Return a unique, stable key for this tab; auto-generate if missing."""
        key = explicit_key or getattr(widget, 'key', None)
        if key:
            if key in self._key_registry:
                raise NavigationError(
                    message=f"Duplicate tab key: {key}",
                    hint="Tab keys must be unique per Notebook."
                )
            return key

        # auto-generate
        while True:
            self._auto_counter += 1
            key = f"tab{self._auto_counter}"
            if key not in self._key_registry:
                return key

    def _to_tab_id(self, tab: Tab) -> str:
        """Resolve Tab handle -> tk tab id."""
        # wrapper widget
        if hasattr(tab, 'tk_name'):
            return cast(Widget, tab).tk_name  # type: ignore[arg-type]

        # index
        if isinstance(tab, int):
            tabs = self.widget.tabs()
            try:
                return tabs[tab]
            except Exception:
                raise NavigationError(
                    message=f"Tab index out of range: {tab}",
                    hint=f"Valid range is 0..{len(tabs) - 1}."
                ) from None

        # key
        if isinstance(tab, str) and tab in self._key_registry:
            return self._key_registry[tab].tk_name

        # fallback: assume tk id string (advanced use)
        if isinstance(tab, str):
            return tab

        raise NavigationError(
            message=f"Unsupported tab reference: {tab!r}",
            hint="Use a tab key (str), index (int), wrapper widget, or tk id."
        )

    def _tab_ref(self, tab_id: str | None) -> dict | None:
        """Public-friendly reference: no tk ids, just index/key/label."""
        if not tab_id:
            return None
        try:
            idx = self.widget.index(tab_id)
        except TclError:
            return None
        key = self._tk_to_key.get(tab_id)
        label = None
        try:
            label = self.widget.tab(tab_id, 'text')
        except Exception:
            pass
        return {"index": idx, "key": key, "label": label}

    # ---- enriched signals ----
    def on_tab_activated(self, handler=None, *, scope="widget"):
        return (self.on(Event.NOTEBOOK_TAB_ACTIVATED, scope=scope).listen(handler)
                if handler else self.on(Event.NOTEBOOK_TAB_ACTIVATED, scope=scope))

    def on_tab_deactivated(self, handler=None, *, scope="widget"):
        return (self.on(Event.NOTEBOOK_TAB_DEACTIVATED, scope=scope).listen(handler)
                if handler else self.on(Event.NOTEBOOK_TAB_DEACTIVATED, scope=scope))

    def on_tab_changed(self, handler: Optional[EventHandler] = None, *, scope="widget") -> Stream[Any] | Self:
        base = self.on(Event.NOTEBOOK_TAB_CHANGED, scope=scope)

        def build_payload(_tk_event):
            current_id = self.widget.select()
            prev_id = self._last_selected
            return {
                "current": self._tab_ref(current_id),
                "previous": self._tab_ref(prev_id),
                "reason": self._last_change_reason or 'unknown',
                "via": self._last_change_via or 'unknown',
            }

        def fire_lifecycle(payload):
            c, p = payload["current"], payload["previous"]
            # compare by stable key (fallback to index if key missing)
            c_key, p_key = (c or {}).get("key"), (p or {}).get("key")
            changed = (c_key != p_key) if (c_key or p_key) else ((c or {}).get("index") != (p or {}).get("index"))
            if p and changed:
                try:
                    self.emit("<<TabDeactivated>>", data={"tab": p})
                except Exception:
                    pass
            if c and changed:
                try:
                    self.emit("<<TabActivated>>", data={"tab": c})
                except Exception:
                    pass

        def commit(payload):
            # keep tk id internally for next diff
            self._last_selected = self.widget.select()
            self._last_change_reason = 'unknown'
            self._last_change_via = 'unknown'

        stream = base.map(build_payload).tap(fire_lifecycle).tap(commit)
        if handler is None:
            return stream
        stream.listen(handler)
        return self

    # ---- tab management (key-based) ----
    def add(self, widget: Widget, *, key: str | None = None, **options: Unpack[NotebookTabOptions]):
        """Add a new tab containing the given widget. Accepts optional stable `key`."""
        # ttk add
        if hasattr(widget, '_tab_options'):
            opts = getattr(widget, '_tab_options') or {}
            self.widget.add(widget.tk_name, **(opts or options))
        else:
            self.widget.add(widget.tk_name, **options)

        # register key <-> widget
        stable_key = self._make_key(widget, key)
        self._key_registry[stable_key] = widget
        self._tk_to_key[widget.tk_name] = stable_key
        return self

    def remove(self, tab: Tab):
        """Remove a tab by key, index, widget, or tk id."""
        self._mark_api_change('forget')
        tab_id = self._to_tab_id(tab)
        # cleanup registries
        key = self._tk_to_key.pop(tab_id, None)
        if key:
            self._key_registry.pop(key, None)
        self.widget.forget(tab_id)
        return self

    def hide(self, tab: Tab):
        """Hide a tab temporarily without removing it."""
        self._mark_api_change('hide')
        self.widget.hide(self._to_tab_id(tab))

    def tab_index(self, tab: Tab) -> int:
        """Return the numeric index of a given tab."""
        return self.widget.index(self._to_tab_id(tab))

    def tab_count(self) -> int:
        """Return the total number of tabs."""
        return self.widget.index('end')

    def select(self, tab: Tab = None):
        """Select a tab (by key/index/widget/tk id) or return the current tk id."""
        if tab is not None:
            self._mark_api_change('api')
            self.widget.select(self._to_tab_id(tab))
            return self
        return self.widget.select()

    def insert(self, position: Literal['end'] | int, widget: Widget, **options: Unpack[NotebookTabOptions]):
        """Insert a tab at the specified position (reorder)."""
        self._mark_api_change('reorder')
        self.widget.insert(position, widget.tk_name, **options)

    def tab_at_coordinate(self, x: int, y: int) -> int:
        """Return the tab index at the given (x, y) coordinate."""
        return self.widget.index(f"@{x},{y}")

    def configure_tab(self, tab: Tab, option: str = None, **options: Unpack[NotebookTabOptions]):
        """Get or set tab configuration options."""
        tab_id = self._to_tab_id(tab)
        if option is not None:
            return self.widget.tab(tab_id, option)
        elif options:
            self.widget.tab(tab_id, **options)
            return self
        else:
            return self

    def tab_list(self) -> list[str]:
        """Return a list of all tk tab identifiers (internal ids)."""
        return self.widget.tabs()

    def enable_keyboard_traversal(self):
        """Enable keyboard navigation between tabs (Ctrl+Tab, etc.)."""
        self.widget.enable_traversal()

    @staticmethod
    def _validate_options(options: dict):
        pass
