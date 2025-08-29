import tkinter
from tkinter import Tk
from typing import Any, List, Tuple, Unpack

# core
from ttkbootstrap.core.layout_context import set_default_root, push_container, pop_container
from ttkbootstrap.core.mixins.container import ContainerMixin
from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.types import PackItemOptions, GridItemOptions
from ttkbootstrap.events import Event
from ttkbootstrap.utils import assert_valid_keys

# exceptions
from ttkbootstrap.exceptions.base import wrap_with_cause
from ttkbootstrap.exceptions.error_bus import ErrorBus
from ttkbootstrap.exceptions.tk_integration import log, normalize_tcl_error

# style
from ttkbootstrap.style import Typography
from ttkbootstrap.style.builders.window import WindowStyleBuilder
from ttkbootstrap.style.theme import ColorTheme
from ttkbootstrap.style.types import ColorMode


class App(BaseWidget, ContainerMixin):
    widget: tkinter.Tk

    def __init__(
            self,
            title: str = "ttkbootstrap",
            theme: ColorMode = "light",
            use_default_fonts: bool = True,
            surface: str = "background",
            fullscreen: bool = False,
            geometry: str | None = None  # "800x600" or "+300+200" or "800x600+300+200"
    ):
        super().__init__(
            tk_widget=Tk,
            tk_widget_options=dict(),
            tk_layout_options=dict(),
            parent=None,
            surface=surface
        )
        self._in_context = True  # only mount children in context

        self.bind_all(Event.ROUTE_DID_MOUNT, lambda _: self._ensure_style_after_routing())

        if geometry:
            self.widget.geometry(geometry)

        if fullscreen:
            self.widget.attributes('-fullscreen', True)

        set_default_root(self)

        # set layout for window container
        self._style_builder = WindowStyleBuilder(self)

        # hide until ready to render
        self.widget.withdraw()
        self.widget.title(title)
        self._theme = ColorTheme.instance(theme)
        self._theme.use(theme)

        # register fonts
        if use_default_fonts:
            Typography.use_fonts()

        self._style_builder.register_style()

        # --- queue for children registered directly on App (root) ---
        self._layout_children: List[Tuple[Any, str, dict]] = []  # (child, method, opts)
        self._in_context: bool = False

        self.widget.report_callback_exception = self.report_callback_exception

    # ----------------------- container semantics -----------------------
    @staticmethod
    def preferred_layout_method() -> str:
        # Root favors pack by convention
        return "pack"

    def _ensure_style_after_routing(self):
        """Ensures that the widget.update_style method is call by setting the theme, which fires the update_style
        on all themed widgets.
        """
        theme = self._theme.name
        self._theme.use(theme)

    def register_layout_child(self, child, method: str, opts: dict):
        """Upsert a child to be mounted when the App context exits or before run()."""
        if method not in ("pack", "grid", "place"):
            return
        for i, (c, m, _) in enumerate(self._layout_children):
            if c is child:
                self._layout_children[i] = (child, method, dict(opts))
                break
        else:
            self._layout_children.append((child, method, dict(opts)))

    def add(self, child, **options: Unpack[PackItemOptions] | Unpack[GridItemOptions]):  # type: ignore[override]
        """Queue a child for immediate or deferred mount on the root.

        If options are empty, derive method from the child's saved layout; otherwise
        infer: absolute/fixed => place, else pack by default.
        """
        method = None
        if hasattr(child, "_saved_layout") and getattr(child, "_saved_layout"):
            method, saved = child._saved_layout  # type: ignore[assignment]
            if not options:
                options = dict(saved)

        if method is None:
            if getattr(child, "_position", "static") in ("absolute", "fixed"):
                method = "place"
            else:
                method = "pack"

        try:
            if method == "pack":
                assert_valid_keys(options, PackItemOptions, where="pack")
            elif method == "grid":
                assert_valid_keys(options, GridItemOptions, where="grid")
        except Exception:
            pass

        self.register_layout_child(child, method, dict(options))  # type: ignore[arg-type]
        if not self._in_context:
            self._mount_queued_children()
        return self

    def _mount_queued_children(self):
        while self._layout_children:
            child, method, opts = self._layout_children.pop(0)
            self._mount_child_root(child, method, **opts)

    def _mount_child_root(self, child, method: str, **opts):
        # (optional) give widgets a chance to validate right before mounting
        if hasattr(child, "_pre_mount_validate"):
            child._pre_mount_validate()

        widget = getattr(child, "widget", child)
        if method == "place":
            if hasattr(child, "attach_place"):
                child.attach_place(**opts)
            elif hasattr(child, "_attach_place"):
                child._attach_place(self.widget, **opts)
            else:
                widget.place(**opts)
            return

        if method == "grid":
            widget.grid(**opts)
        else:
            widget.pack(**opts)

    # ----------------------- context manager -----------------------
    def __enter__(self):
        self._in_context = True
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            # mount queued children (validation errors surface here)
            self._mount_queued_children()
            self.widget.update_idletasks()
            self.widget.deiconify()
        finally:
            self._in_context = False
            pop_container()
        return False

    # ----------------------- theming & lifecycle -----------------------
    @property
    def theme(self):
        return self._theme

    def geometry(self, *args):
        self.widget.geometry(*args)
        return self

    def surface(self, value=None):
        if value is None:
            return self._surface_token
        else:
            self._surface_token = value
            self.theme.update_theme_styles()
            return self

    @property
    def _bind(self, *args):
        return self.widget._bind

    @property
    def surface_token(self):
        return self._surface_token

    def run(self):
        self._mount_queued_children()
        self.widget.update_idletasks()
        self.widget.update()
        self.widget.deiconify()
        return self.widget.mainloop()

    def quit(self):
        self.widget.quit()

    @classmethod
    def report_callback_exception(cls, exc, val, tb):
        # Log the real traceback:
        log.exception("Tk callback failed", exc_info=(exc, val, tb))
        # Emit a friendly error with the original exception as the cause:
        if exc is tkinter.TclError:
            ErrorBus.emit(wrap_with_cause(str(normalize_tcl_error(val)), val))
        else:
            ErrorBus.emit(wrap_with_cause("Unexpected internal error", val))
