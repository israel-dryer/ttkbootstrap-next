from __future__ import annotations

import reprlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Tuple

from ttkbootstrap_next.interop.runtime.key_resolver import decode_mods, resolve_press_from_parts


def _repr_data_preview(d: dict) -> str:
    # uses python’s smart truncation, still calls _normalize first
    return reprlib.Repr().repr(_normalize(d))


def _normalize(x: Any) -> Any:
    try:
        if isinstance(x, Enum):
            return x.value
        if isinstance(x, Mapping):
            return {k: _normalize(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            T = type(x)
            return T(_normalize(v) for v in x)
        if isinstance(x, (bytes, bytearray, memoryview)):
            return bytes(x).decode("utf-8", "replace")
        if isinstance(x, set):
            return sorted(_normalize(v) for v in x)
        return x
    except Exception:
        # Always fall back to a safe representation
        return repr(x)


@dataclass(slots=True)
class BaseEvent:
    name: str
    target: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[str] = None
    toplevel: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"name": self.name, "data": _normalize(self.data)}
        if self.target is not None: out["target"] = self.target
        if self.timestamp is not None: out["timestamp"] = self.timestamp
        if self.toplevel is not None: out["root"] = self.toplevel
        return out

    def __repr__(self) -> str:
        parts = [f"name={self.name!r}"]
        if self.target is not None:    parts.append(f"target={self.target!r}")
        if self.timestamp is not None: parts.append(f"timestamp={self.timestamp!r}")
        if self.toplevel is not None:  parts.append(f"root={self.toplevel!r}")
        parts.append(f"data={_repr_data_preview(self.data)}")
        return f"{self.__class__.__name__}(" + ", ".join(parts) + ")"

    __str__ = __repr__


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
    screen_x: Optional[int] = None
    screen_y: Optional[int] = None
    state: Optional[int] = None


@dataclass(slots=True)
class MotionEvent(BaseEvent):
    x: Optional[int] = None
    y: Optional[int] = None
    screen_x: Optional[int] = None
    screen_y: Optional[int] = None
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
