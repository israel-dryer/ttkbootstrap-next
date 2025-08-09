from typing import Any

_layout_context_stack = []
_default_root = None


def default_root():
    return _default_root


def set_default_root(app: Any):
    global _default_root
    _default_root = app


def current_layout():
    return _layout_context_stack[-1] if _layout_context_stack else default_root()


def layout_context_stack():
    return _layout_context_stack
