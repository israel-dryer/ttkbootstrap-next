"""
interop.spec.profiles
---------------------

Spec-only definitions for per-event field selection and the corresponding
Tcl substitution strings. This module intentionally does **not** import
anything from the runtime layer.

Rules:
- Physical events (mouse/keyboard/motion/configure) map to minimal field sets.
- **Any virtual event** (name starts with '<<' and ends with '>>') uses the
  'widget' profile by default (only '%W').
  If you later need custom payloads from `event_generate -data`, change the
  'virtual' profile in _FIELDS to include "data" as well (e.g., ["widget","data"]).
"""

from __future__ import annotations

from functools import lru_cache
from typing import Dict, List

from ttkbootstrap.interop.spec.subs import Sub, event_subs

# Build a fast lookup: field name -> Sub (for its %code)
_SUB_BY_NAME: Dict[str, Sub] = {s.name: s for s in event_subs}

# Patterns → fields to request from Tcl (order matters)
_FIELDS: Dict[str, List[str]] = {
    "key": ["keysym", "char", "state", "widget"],
    "button": ["x", "y", "x_root", "y_root", "state", "widget"],
    "motion": ["x", "y", "x_root", "y_root", "state", "widget"],
    "wheel": ["delta", "x", "y", "widget"],
    "configure": ["width", "height", "x", "y", "widget"],
    "widget": ["widget"],
    "virtual": ["data", "timestamp", "widget"]
}

# Physical event sequence → pattern
_GROUP: Dict[str, str] = {
    # keyboard (generic & specific transitions)
    "<KeyPress>": "key",
    "<KeyRelease>": "key",
    "<Return>": "key",
    "<Tab>": "key",
    "<Escape>": "key",
    "<KeyPress-Return>": "key",
    "<KeyRelease-Return>": "key",
    "<KeyPress-Tab>": "key",
    "<KeyRelease-Tab>": "key",
    "<KeyPress-Escape>": "key",
    "<KeyRelease-Escape>": "key",

    # mouse buttons
    "<Button-1>": "button",
    "<Button-2>": "button",
    "<Button-3>": "button",
    "<Double-Button-1>": "button",
    "<ButtonPress>": "button",
    "<ButtonRelease>": "button",

    # wheel
    "<MouseWheel>": "wheel",
    "<Button-4>": "button",  # linux/X11 wheel up (optionally synthesize delta in runtime)
    "<Button-5>": "button",  # linux/X11 wheel down

    # motion/drag
    "<Motion>": "motion",
    "<B1-Motion>": "motion",

    # configure
    "<Configure>": "configure",

    # enter/leave/focus/map/etc. → usually widget-only
    "<Enter>": "widget",
    "<Leave>": "widget",
    "<FocusIn>": "widget",
    "<FocusOut>": "widget",
    "<Map>": "widget",
    "<Unmap>": "widget",
    "<Visibility>": "widget",
    "<Expose>": "widget",
    "<Destroy>": "widget",
}


@lru_cache(maxsize=256)
def pattern_for(event_name: str) -> str:
    """
    Return the pattern key for a given event sequence.

    Virtual events (e.g., '<<Change>>') are treated as 'virtual' by default.
    """
    # Fast-path virtuals: "<<...>>"
    if len(event_name) >= 4 and event_name.startswith("<<") and event_name.endswith(">>"):
        # If you adopt a richer virtual profile later, return "virtual" here instead.
        return "virtual"
    return _GROUP.get(event_name, "key")


@lru_cache(maxsize=256)
def fields_for(event_name: str) -> List[str]:
    """Return the ordered field names to request from Tcl for this event."""
    return _FIELDS[pattern_for(event_name)]


@lru_cache(maxsize=256)
def event_substring(event_name: str) -> str:
    """Return the Tcl substitution substring (e.g., '%x %y %X %Y %W')."""
    names = fields_for(event_name)
    return " ".join(_SUB_BY_NAME[n].code for n in names)
