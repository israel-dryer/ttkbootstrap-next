from tkinter import TclError, ttk
from typing import Any, Literal, Optional, Unpack, cast

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.core.layout_context import pop_container, push_container
from ttkbootstrap.events import Event
from ttkbootstrap.exceptions.base import NavigationError
from ttkbootstrap.interop.runtime.binding import Stream
from ttkbootstrap.interop.runtime.event_types import BaseEvent
from ttkbootstrap.types import Widget
from ttkbootstrap.widgets.notebook.events import (
    NotebookChangedEvent,
    NotebookTabActivatedEvent,
    NotebookTabDeactivatedEvent
)
from ttkbootstrap.widgets.notebook.style import NotebookStyleBuilder
from ttkbootstrap.widgets.notebook.tab import Tab, TabGrid, TabPack
from ttkbootstrap.widgets.notebook.types import (
    ChangeMethod, ChangeReason, NotebookChangedData,
    NotebookOptions, NotebookTabOptions, TabRef
)


class Notebook(BaseWidget):
    """Wrapper around ttk.Notebook with stable key-based tab identity."""
    Pack = TabPack
    Grid = TabGrid
    widget: ttk.Notebook

    def __init__(self, **kwargs: Unpack[NotebookOptions]):
        """
        Create a Notebook widget and initialize tab identity/state tracking.

        Keyword Args:
            take_focus: Accepts keyboard focus during traversal.
            width: Width of the notebook in pixels.
            height: Height of the notebook in pixels.
            id: A unique identifier used to query this widget.
            padding: Internal padding around the content area.
            parent: The parent container of this widget.
            position: The `place` container position.
        """
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
        self._last_change_reason: ChangeReason = ChangeReason.UNKNOWN
        self._last_change_via: ChangeMethod = ChangeMethod.UNKNOWN

    # ---- context ----
    def __enter__(self):
        """Enter the layout context: push this notebook as the current container."""
        push_container(self)
        self._in_context = True
        return self

    def __exit__(self, exc_type, exc, tb):
        """Exit the layout context: pop this notebook from the container stack."""
        pop_container()
        self._in_context = False

    # ---- internal helpers ----
    def _mark_api_change(self, reason: str = ChangeReason.API):
        """Record a programmatic change reason so the next change event can report it."""
        self._last_change_reason = reason
        self._last_change_via = ChangeMethod.PROGRAMMATIC

    def _make_key(self, widget: Widget, explicit_key: Optional[str]) -> str:
        """Return a unique, stable key for a tab; auto-generate (`tabN`) if none provided."""
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
        """Resolve a tab reference (key/index/widget/tk-id) to a Tk tab id."""
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

    def _tab_ref(self, tab_id: str | None) -> TabRef | None:
        """Return a simplified tab reference ({index,key,label}) or None if invalid."""
        ref: TabRef = {"index": None, "key": None, "label": None}
        if not tab_id:
            return None
        try:
            ref['index'] = self.widget.index(tab_id)
            ref['label'] = self.widget.tab(tab_id, 'text')
        except TclError:
            return None
        ref['key'] = self._tk_to_key.get(tab_id)
        return ref

    # ---- enriched signals ----
    def on_tab_activated(self) -> Stream[NotebookTabActivatedEvent]:
        """Convenience alias for the notebook tab activated stream"""
        return self.on(Event.NOTEBOOK_TAB_ACTIVATED)

    def on_tab_deactivated(self) -> Stream[NotebookTabDeactivatedEvent]:
        """Convenience alias for the notebook tab deactivated stream"""
        return self.on(Event.NOTEBOOK_TAB_DEACTIVATED)

    def on_tab_changed(self) -> Stream[NotebookChangedEvent]:
        """Convenience alias for the notebook tab changed stream

        Emits:
            - <<TkbNotebookTabChanged>>
            - <<TkbNotebookTabActivated>>
            - <<TkbNotebookTabDeactivated>>

        The stream maps the raw `BaseEvent` into a `NotebookChangedEvent` whose
        `.data` payload contains:
            - `current`: TabRef | None
            - `previous`: TabRef | None
            - `reason`: ChangeReason
            - `via`: ChangeMethod
        """
        base: Stream[BaseEvent] = self.on(Event.NOTEBOOK_TAB_CHANGED)

        def build_payload(ev: BaseEvent) -> NotebookChangedEvent:
            """Attach the NotebookChangedData payload to the event."""
            payload: NotebookChangedData = {
                "current": self._tab_ref(self.widget.select()),
                "previous": self._tab_ref(self._last_selected),
                "reason": self._last_change_reason or ChangeReason.UNKNOWN,
                "via": self._last_change_via or ChangeMethod.UNKNOWN,
            }
            ev.data = cast(dict[str, Any], payload)
            return cast(NotebookChangedEvent, ev)

        def fire_lifecycle(ev: NotebookChangedEvent) -> None:
            """Emit per-tab lifecycle events when selection truly changes."""
            c, p = ev.data["current"], ev.data["previous"]
            c_key, p_key = (c or {}).get("key"), (p or {}).get("key")
            changed = (c_key != p_key) if (c_key or p_key) else ((c or {}).get("index") != (p or {}).get("index"))
            if p and changed:
                self.emit(Event.NOTEBOOK_TAB_DEACTIVATED, data={"tab": p})
            if c and changed:
                self.emit(Event.NOTEBOOK_TAB_ACTIVATED, data={"tab": c})

        def commit(_ev: NotebookChangedEvent) -> None:
            """Reset change-tracking fields after dispatching the change event."""
            self._last_selected = self.widget.select()
            self._last_change_reason = ChangeReason.UNKNOWN
            self._last_change_via = ChangeMethod.UNKNOWN

        return base.map(build_payload).tap(fire_lifecycle).tap(commit)

    # ---- tab management (key-based) ----
    def add(self, widget: Widget, *, key: str | None = None, **options: Unpack[NotebookTabOptions]):
        """Add a widget as a new tab, register its stable key, and return self."""
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
        """Forget a tab (by key/index/widget/tk-id), clean registries, and return self."""
        self._mark_api_change(ChangeReason.FORGET)
        tab_id = self._to_tab_id(tab)
        # cleanup registries
        key = self._tk_to_key.pop(tab_id, None)
        if key:
            self._key_registry.pop(key, None)
        self.widget.forget(tab_id)
        return self

    def hide(self, tab: Tab):
        """Hide a tab without removing it; selection may change implicitly."""
        self._mark_api_change(ChangeReason.HIDE)
        self.widget.hide(self._to_tab_id(tab))

    def tab_index(self, tab: Tab) -> int:
        """Return the current position (index) of a tab."""
        return self.widget.index(self._to_tab_id(tab))

    def tab_count(self) -> int:
        """Return the total number of tabs in the notebook."""
        return self.widget.index('end')

    def select(self, tab: Tab = None):
        """Select a tab (setter) or return the current Tk tab id (getter)."""
        if tab is not None:
            self._mark_api_change(ChangeReason.API)
            self.widget.select(self._to_tab_id(tab))
            return self
        return self.widget.select()

    def insert(self, position: Literal['end'] | int, widget: Widget, **options: Unpack[NotebookTabOptions]):
        """Insert an existing tab at a new position (reorder)."""
        self._mark_api_change(ChangeReason.REORDER)
        self.widget.insert(position, widget.tk_name, **options)

    def tab_at_coordinate(self, x: int, y: int) -> int:
        """Return the index of the tab under window coordinates (x, y)."""
        return self.widget.index(f"@{x},{y}")

    def configure_tab(self, tab: Tab, option: str = None, **options: Unpack[NotebookTabOptions]):
        """Get or set ttk tab options for a specific tab."""
        tab_id = self._to_tab_id(tab)
        if option is not None:
            return self.widget.tab(tab_id, option)
        elif options:
            self.widget.tab(tab_id, **options)
            return self
        else:
            return self

    def tab_list(self) -> list[str]:
        """Return the list of Tk tab identifiers (internal ids)."""
        return self.widget.tabs()

    def enable_keyboard_traversal(self):
        """Enable Ctrl+Tab/Shift+Ctrl+Tab keyboard traversal between tabs."""
        self.widget.enable_traversal()

    @staticmethod
    def _validate_options(options: dict):
        """Reserved for child-layout option validation (no-op for now)."""
        pass
