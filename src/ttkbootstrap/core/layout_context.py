# Simple container stack to infer parents inside with-blocks
from typing import Any

_context_stack = []

_default_root = None


def default_root():
    return _default_root


def set_default_root(app: Any):
    global _default_root
    _default_root = app


def push_container(c):
    _context_stack.append(c)


def pop_container():
    try:
        _context_stack.pop()
    except IndexError:
        pass


def has_current_container():
    return bool(_context_stack)


def current_container():
    if not _context_stack:
        return default_root()
    return _context_stack[-1]
