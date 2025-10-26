from typing import Callable, TypeVar

T = TypeVar("T")


def delegates_layout_context(attr: str) -> Callable[[type[T]], type[T]]:
    """
    Class decorator that forwards `with`-context to a child container attribute.

    Usage:
        @delegates_layout_context("_body")
        class Fieldset(Grid):
            def __init__(...):
                ...
                self._body = Pack(parent=self).attach(sticky="nsew", column=0, row=1)
                # Ensure `_body` exists by the time __enter__ is called.

    The `with ... as x:` binding remains the parent instance; children created
    inside the block are routed to the child's context (so automount works).
    """

    def deco(cls: type[T]) -> type[T]:
        def __enter__(self):
            child = getattr(self, attr, None)
            if child is None:
                raise AttributeError(
                    f"{cls.__name__} has no attribute {attr!r} at __enter__ time."
                )
            child.__enter__()
            return self  # keep `as` bound to the parent

        def __exit__(self, exc_type, exc, tb):
            child = getattr(self, attr, None)
            if child is None:
                # nothing to unwind; propagate exception handling default
                return False
            return child.__exit__(exc_type, exc, tb)

        cls.__enter__ = __enter__
        cls.__exit__ = __exit__
        return cls

    return deco
