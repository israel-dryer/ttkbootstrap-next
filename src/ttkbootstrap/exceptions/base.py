from __future__ import annotations
from typing import Any, Optional

__all__ = [
    "UIError", "LayoutError", "ThemeError", "ConfigError", "StateError",
    "InvalidThemeError", "InvalidTokenError",
    "with_note", "wrap_with_cause", "NavigationError"
]


# ---------------------------
# Base & common specializations
# ---------------------------

class UIError(Exception):
    """Base for all ttkbootstrap errors."""
    __slots__ = ("hint", "code", "widget_id")

    def __init__(
            self, message: str, *, hint: Optional[str] = None,
            code: Optional[str] = None, widget_id: Optional[str] = None):
        super().__init__(message)
        self.hint = hint
        self.code = code
        self.widget_id = widget_id

    def __str__(self) -> str:
        base = super().__str__()
        if self.hint:
            return f"{base} — Hint: {self.hint}"
        return base


class LayoutError(UIError): ...


class ThemeError(UIError): ...


class ConfigError(UIError): ...


class StateError(UIError): ...


class NavigationError(UIError): ...


# ---------------------------
# Back-compat shims (keep your names)
# ---------------------------

class InvalidThemeError(ThemeError):
    """Raised when a user-provided theme is invalid (compat)."""
    __slots__ = ("theme_name",)

    def __init__(
            self, message: str, theme_name: str | None = None, *,
            hint: str | None = None):
        full = f"Invalid theme '{theme_name}': {message}" if theme_name else f"Invalid theme: {message}"
        super().__init__(full, hint=hint, code="THEME_INVALID")
        self.theme_name = theme_name


class InvalidTokenError(ConfigError):
    """Raised when an invalid style token is provided (compat)."""
    __slots__ = ("token",)

    def __init__(
            self, message: str, token: str | None = None, *,
            hint: str | None = None):
        full = f"Invalid style token '{token}': {message}" if token else f"Invalid style token: {message}"
        super().__init__(full, hint=hint, code="TOKEN_INVALID")
        self.token = token


# ---------------------------
# Small helpers for nicer call sites
# ---------------------------

def with_note(err: BaseException, note: str) -> BaseException:
    """Attach an add_note() (Py 3.11+) if available; return the same exception."""
    try:
        err.add_note(note)  # type: ignore[attr-defined]
    except Exception:
        pass
    return err


def wrap_with_cause(message: str, cause: BaseException, cls: type[UIError] = UIError, **kw: Any) -> UIError:
    """
    Build a UIError (or subclass) that keeps the original as __cause__
    without using 'raise ... from ...' (useful when you're emitting).
    """
    err = cls(message, **kw)
    err.__cause__ = cause
    return err
