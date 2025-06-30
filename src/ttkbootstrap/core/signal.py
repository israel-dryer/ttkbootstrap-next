import tkinter as tk
from typing import Callable, Generic, Type, TypeVar, Any, Tuple
from itertools import count
from .libtypes import TraceOperationType

T = TypeVar("T")
U = TypeVar("U")


class _SignalTrace:
    """
    Internal helper to manage Tcl variable traces using tkinter's Variable API.
    This class encapsulates low-level `trace_add` and `trace_remove` logic.
    """

    def __init__(self, tk_var: tk.Variable):
        """
        Initialize a trace manager for a tkinter variable.

        Args:
            tk_var: A tkinter.Variable instance (e.g., StringVar, IntVar).
        """
        self._var = tk_var
        self._traces: dict[str, Callable[..., Any]] = {}

    def callbacks(self) -> Tuple[str, ...]:
        """
        Return all currently active trace IDs.

        Returns:
            A tuple of trace ID strings.
        """
        return tuple(self._traces.keys())

    def add(
        self,
        operation: TraceOperationType,
        callback: Callable[[T], Any],
        get_value: Callable[[], T],
    ) -> str:
        """
        Add a new trace that calls a callback when the variable is written.
        """
        def traced_callback(name: str, index: str, mode: str) -> None:
            callback(get_value())

        fid = self._var.trace_add(operation, traced_callback)
        self._traces[fid] = traced_callback
        return fid

    def remove(self, operation: TraceOperationType, fid: str):
        """
        Remove a trace by ID.
        """
        self._var.trace_remove(operation, fid)
        self._traces.pop(fid, None)


class Signal(Generic[T]):
    """
    A reactive signal backed by a tkinter Variable.

    Supports value access, transformation via `.map()`, and subscription
    to change events via `.subscribe()`.

    Can be passed to Tkinter widgets using `str(signal)` or `signal.name`.
    """

    _cnt = count(1)

    def __init__(self, value: T, name: str | None = None):
        self._name = name or f"SIG{next(self._cnt)}"
        self._type: Type[T] = type(value)
        self._var = self._create_variable(value)
        self._trace = _SignalTrace(self._var)
        self._subscribers: dict[Callable[[T], None], str] = {}

    def _create_variable(self, value: T) -> tk.Variable:
        if isinstance(value, bool):
            return tk.BooleanVar(name=self._name, value=value)
        elif isinstance(value, int):
            return tk.IntVar(name=self._name, value=value)
        elif isinstance(value, float):
            return tk.DoubleVar(name=self._name, value=value)
        else:
            return tk.StringVar(name=self._name, value=value)

    def __call__(self) -> T:
        """
        Get the current value of the signal.

        Returns:
            The current typed value.
        """
        return self._var.get()

    def set(self, value: T):
        """
        Set the signal to a new value and notify subscribers.

        Args:
            value: The new value. Must match the original type.

        Raises:
            TypeError: If the value type does not match the original.
        """
        if not isinstance(value, self._type):
            raise TypeError(f"Expected {self._type.__name__}, got {type(value).__name__}")
        self._var.set(value)

    def map(self, transform: Callable[[T], U]) -> 'Signal[U]':
        """
        Create a derived signal that transforms this signal's value.

        Args:
            transform: A function applied to the current and future values.

        Returns:
            A new Signal[U] that stays updated with the transformed value.
        """
        derived = Signal(transform(self()))

        def update(value: T):
            derived.set(transform(value))

        self.subscribe(update)
        return derived

    def subscribe(self, callback: Callable[[T], Any]):
        """
        Subscribe to value changes of this signal.

        Args:
            callback: A function that receives the current value (T) when updated.

        Returns:
            A trace ID that can be used for removal.
        """
        fid = self._trace.add("write", callback, self)
        self._subscribers[callback] = fid
        return fid

    def unsubscribe(self, callback: Callable[[T], Any]):
        """
        Remove a previously registered subscriber.

        Args:
            callback: The function originally passed to `subscribe()`.
        """
        if callback in self._subscribers:
            fid = self._subscribers.pop(callback)
            self._trace.remove("write", fid)

    def unsubscribe_all(self):
        """
        Remove all currently subscribed callbacks.
        """
        for fid in self._subscribers.values():
            self._trace.remove("write", fid)
        self._subscribers.clear()

    def __getattr__(self, name):
        """
        Proxy access to the underlying tk.Variable instance.
        """
        return getattr(self._var, name)

    @property
    def name(self) -> str:
        """
        Return the Tcl name of the variable (for use in widget `textvariable`).
        """
        return self._name

    @property
    def type(self) -> Type:
        """
        The original type of the signal value.

        Returns:
            A Python type (e.g., int, str).
        """
        return self._type

    def __str__(self):
        return self._name

    def __repr__(self):
        return f"<Signal name={self._name} type={self._type.__name__}>"
