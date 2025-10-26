from __future__ import annotations
import sys
from dataclasses import dataclass
from typing import Optional, Iterable, List

# Tk state bits
SHIFT = 0x0001
LOCK = 0x0002
CONTROL = 0x0004
MOD1 = 0x0008
MOD2 = 0x0010
MOD3 = 0x0020
MOD4 = 0x0040
MOD5 = 0x0080

_PRETTY = {
    "Return": "Enter", "Escape": "Esc", "BackSpace": "Backspace",
    "Prior": "PageUp", "Next": "PageDown",
    "KP_Add": "Num+", "KP_Subtract": "Num-", "KP_Multiply": "Num*", "KP_Divide": "Num/", "KP_Enter": "NumEnter",
    "space": "Space", "minus": "-", "equal": "=", "bracketleft": "[", "bracketright": "]",
    "semicolon": ";", "apostrophe": "'", "grave": "`", "backslash": "\\", "slash": "/", "comma": ",", "period": ".",
}

_MODIFIER_KEYSYMS = {
    "Shift_L": "Shift", "Shift_R": "Shift",
    "Control_L": "Control", "Control_R": "Control",
    "Alt_L": "Alt", "Alt_R": "Alt", "Option_L": "Alt", "Option_R": "Alt",
    "Command": "Cmd", "Super_L": "Super", "Super_R": "Super", "Meta_L": "Meta", "Meta_R": "Meta",
    "ISO_Level3_Shift": "AltGr", "Mode_switch": "AltGr",
}

_ORDER = ("Shift", "Ctrl", "Alt", "AltGr", "Cmd", "Super", "Meta", "Caps")


def _is_win(): return sys.platform.startswith("win")


def _is_mac(): return sys.platform == "darwin"


def _dedup(seq: Iterable[str]) -> List[str]:
    seen = set()
    out = []
    for s in seq:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _sort_mods(mods: List[str]) -> List[str]:
    order = {n: i for i, n in enumerate(_ORDER)}
    return sorted(mods, key=lambda m: order.get(m, 999))


def _keysym_is_alt(ks: Optional[str]) -> bool:
    return ks in {"Alt_L", "Alt_R", "Option_L", "Option_R"}


def _altgr_windows(state: int, keysym: Optional[str]) -> bool:
    return _is_win() and (state & CONTROL) and (state & MOD1) and not _keysym_is_alt(keysym)


def decode_mods(state: int | None, *, keysym: Optional[str] = None, include_caps: bool = False) -> List[str]:
    """Meaningful modifiers from state+keysym; never exposes Mod1...Mod5."""
    if not isinstance(state, int):
        return []
    mods: List[str] = []
    if state & SHIFT: mods.append("Shift")
    if state & CONTROL: mods.append("Ctrl")
    if include_caps and (state & LOCK): mods.append("Caps")

    # AltGr first (avoid Ctrl+Alt noise)
    if keysym in ("ISO_Level3_Shift", "Mode_switch") or (state & MOD5 and not _is_mac()):
        mods.append("AltGr")
    elif _altgr_windows(state, keysym):
        if "Ctrl" in mods: mods.remove("Ctrl")
        mods.append("AltGr")
    else:
        if _keysym_is_alt(keysym):
            mods.append("Alt")

    if keysym == "Command": mods.append("Cmd")
    if keysym in ("Super_L", "Super_R"): mods.append("Super")
    if keysym in ("Meta_L", "Meta_R"): mods.append("Meta")

    return _sort_mods(_dedup(mods))


def _normalize_base(keysym: Optional[str], char: Optional[str]) -> Optional[str]:
    if keysym:
        base = _PRETTY.get(keysym, keysym)
        if len(base) == 1: return base.upper()
        return base
    if char:
        c = char.strip()
        if not c: return None
        return c.upper() if len(c) == 1 else c
    return None


@dataclass(frozen=True)
class Press:
    base: str
    mods: List[str]
    keysym: Optional[str]
    state: int

    def as_string(self) -> str:
        return "+".join([*self.mods, self.base]) if self.mods else self.base


def resolve_press_from_parts(
        *, state: int | None, keysym: Optional[str], char: Optional[str], include_caps: bool = False) -> Optional[
    Press]:
    """Resolve from loose parts (works with your namedtuple dict)."""
    # If the pressed key itself is a modifier, wait for the base key.
    if keysym in _MODIFIER_KEYSYMS:
        return None
    base = _normalize_base(keysym, char)
    if not base:
        return None
    mods = decode_mods(state or 0, keysym=keysym, include_caps=include_caps)
    return Press(base=base, mods=mods, keysym=keysym, state=int(state or 0))
