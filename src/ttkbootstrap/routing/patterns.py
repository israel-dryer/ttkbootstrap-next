from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Dict, Pattern, Tuple, Optional

_SEGMENT = r"(?P<{name}>[^/]+)"
_WILDCARD = r"(?P<wildcard>.*)"


@dataclass(frozen=True)
class CompiledPattern:
    pattern: str
    regex: Pattern[str]
    param_names: Tuple[str, ...]


def compile_pattern(pattern: str) -> CompiledPattern:
    if not pattern.startswith("/"):
        pattern = "/" + pattern
    param_names = []
    parts = pattern.rstrip("/").split("/")
    rx_parts = []
    for p in parts:
        if p.startswith(":"):
            name = p[1:]
            param_names.append(name)
            rx_parts.append(_SEGMENT.format(name=name))
        elif p == "*":
            rx_parts.append(_WILDCARD)
        else:
            rx_parts.append(re.escape(p))
    rx = "^" + "/".join(rx_parts) + "/?$"
    return CompiledPattern(pattern=pattern, regex=re.compile(rx), param_names=tuple(param_names))


def match_path(compiled: CompiledPattern, path: str) -> Optional[Dict[str, str]]:
    if not path.startswith("/"):
        path = "/" + path
    m = compiled.regex.match(path)
    if not m:
        return None
    params = {name: m.group(name) for name in compiled.param_names if m.groupdict().get(name) is not None}
    if "wildcard" in m.groupdict() and m.group("wildcard") is not None:
        params["*"] = m.group("wildcard")
    return params
