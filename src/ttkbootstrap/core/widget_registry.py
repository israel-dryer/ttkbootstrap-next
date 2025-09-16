# ttkbootstrap/types_registry.py
from __future__ import annotations, annotations

from threading import RLock
from tkinter import Widget
from typing import Any, Iterable, Optional, Protocol, runtime_checkable
from weakref import WeakKeyDictionary, WeakValueDictionary, ref

from ttkbootstrap.events import Event
from ttkbootstrap.types import Widget  # your Tk/ttk widget alias


@runtime_checkable
class SupportsRegistry(Protocol):
    @property
    def tk_name(self) -> str: ...

    @property
    def widget(self) -> Widget: ...


_by_tk: WeakValueDictionary[str, SupportsRegistry] = WeakValueDictionary()
_by_id: WeakValueDictionary[str, SupportsRegistry] = WeakValueDictionary()
_widget_to_id: WeakKeyDictionary[SupportsRegistry, str] = WeakKeyDictionary()
_lock = RLock()


def register(widget: SupportsRegistry, *, custom_id: str | None = None) -> None:
    """Insert a widget into the registry by its tk_name and optional custom id."""
    with _lock:
        _by_tk[widget.tk_name] = widget
        if custom_id:
            _claim_id(widget, custom_id)

        # Auto-unregister on destroy (safe: add="+", fires once for the widget itself)
        try:
            widget.on(Event.DESTROY).listen(lambda e, w_ref=ref(widget): _on_destroy(w_ref()), add="+")
        except Exception:
            # If bind is not available (very rare), it's still safe; GC will prune.
            pass


def unregister(widget: SupportsRegistry) -> None:
    """Remove a widget from all indices, if present."""
    with _lock:
        try:
            if _by_tk.get(widget.tk_name) is widget:
                del _by_tk[widget.tk_name]
        except Exception:
            pass

        old_id = _widget_to_id.pop(widget, None)
        if old_id and _by_id.get(old_id) is widget:
            del _by_id[old_id]


def set_id(widget: SupportsRegistry, new_id: str | None) -> None:
    """Assign (or clear) a custom id for this widget."""
    with _lock:
        # Clear previous id (if any)
        old = _widget_to_id.pop(widget, None)
        if old and _by_id.get(old) is widget:
            del _by_id[old]
        # Set new id
        if new_id:
            _claim_id(widget, new_id)


def get_id(widget: SupportsRegistry) -> Optional[str]:
    """Return the widget's current custom id, if any."""
    return _widget_to_id.get(widget)


def by_tk(tk_name: str) -> Optional[Any]:
    """Lookup by Tcl/Tk pathname (e.g., '.!frame.!button')."""
    return _by_tk.get(tk_name)


def by_id(custom_id: str) -> Optional[Any]:
    """Lookup by custom id."""
    return _by_id.get(custom_id)


def lookup(key: str) -> Optional[Any]:
    """Lookup a widget by either tk_name or id."""
    # Tk widget path_names always start with "."
    if key and key[0] == ".":
        return _by_tk.get(key)
    # otherwise treat it as a custom id
    w = _by_id.get(key)
    return w if w is not None else _by_tk.get(key)  # rare fallback


def all_widgets_snapshot() -> Iterable[SupportsRegistry]:
    """Return a snapshot (list) of currently tracked widgets."""
    # WeakValueDictionary is live; make a stable copy
    return list(_by_tk.values())


# ---- internals ----
def _on_destroy(widget: Optional[SupportsRegistry]) -> None:
    if widget is not None:
        unregister(widget)


def _claim_id(widget: SupportsRegistry, cid: str) -> None:
    # If someone else had this id, we simply move it (last write wins).
    prev = _by_id.get(cid)
    if prev is not None and prev is not widget:
        try:
            # Remove prev's reverse mapping if it pointed here
            if _widget_to_id.get(prev) == cid:
                del _widget_to_id[prev]
        except Exception:
            pass
    _by_id[cid] = widget
    _widget_to_id[widget] = cid
