# interop/runtime/event_types.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from ttkbootstrap.interop.runtime.key_resolver import decode_mods, resolve_press_from_parts


@dataclass(slots=True)
class BaseEvent:
    name: str
    widget: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[str] = None
    root: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"name": self.name, "data": self.data}
        if self.widget is not None: out["widget"] = self.widget
        if self.timestamp is not None: out["timestamp"] = self.timestamp
        if self.root is not None: out["root"] = self.root
        return out


# --- keyboard / key-like ---------------------------------------------------
@dataclass(slots=True)
class KeyEvent(BaseEvent):
    keysym: Optional[str] = None
    char: Optional[str] = None
    state: Optional[int] = None
    _mods: Optional[Tuple[str, ...]] = None
    _press: Optional[str] = None

    @property
    def mods(self) -> Tuple[str, ...]:
        if self._mods is None:
            m = decode_mods(self.state, keysym=self.keysym, include_caps=False)
            self._mods = tuple(m) if m else ()
        return self._mods

    @property
    def press(self) -> Optional[str]:
        if self._press is None:
            p = resolve_press_from_parts(state=self.state, keysym=self.keysym, char=self.char, include_caps=False)
            self._press = p.as_string() if p else None
        return self._press

    def to_dict(self) -> Dict[str, Any]:
        out = super().to_dict()
        if self.keysym is not None: out["keysym"] = self.keysym
        if self.char is not None: out["char"] = self.char
        if self.state is not None: out["state"] = self.state
        if self._mods is not None: out["mods"] = self._mods
        if self._press is not None: out["press"] = self._press
        return out


# --- mouse buttons / motion / drag ----------------------------------------
@dataclass(slots=True)
class ButtonEvent(BaseEvent):
    x: Optional[int] = None
    y: Optional[int] = None
    x_root: Optional[int] = None
    y_root: Optional[int] = None
    state: Optional[int] = None


@dataclass(slots=True)
class MotionEvent(BaseEvent):
    x: Optional[int] = None
    y: Optional[int] = None
    x_root: Optional[int] = None
    y_root: Optional[int] = None
    state: Optional[int] = None


# --- wheel -----------------------------------------------------------------
@dataclass(slots=True)
class WheelEvent(BaseEvent):
    delta: Optional[float] = None
    x: Optional[int] = None
    y: Optional[int] = None


# --- configure -------------------------------------------------------------
@dataclass(slots=True)
class ConfigureEvent(BaseEvent):
    width: Optional[int] = None
    height: Optional[int] = None
    x: Optional[int] = None
    y: Optional[int] = None


# --- simple widget-only / virtual -----------------------------------------
@dataclass(slots=True)
class WidgetEvent(BaseEvent):
    pass


# --- fallback --------------------------------------------------------------
@dataclass(slots=True)
class UnknownEvent(BaseEvent):
    raw: Dict[str, Any] = field(default_factory=dict)
