# ttkbootstrap/routing/outlet.py
from __future__ import annotations
from typing import Dict, Any
from ttkbootstrap.layouts.pack import Pack
from .router import Router, Route

def _payload(path: str, params: Dict[str, str]) -> Dict[str, Any]:
    # Custom event payload (dict)
    return {"path": path, "params": params}

class RouterOutlet(Pack):
    def __init__(self, *, name: str = None, **kwargs):
        super().__init__(**kwargs)
        self._outlet_name = name
        self._router: Router | None = None
        self._active_view = None
        self._finalize_token = None

        self._set_router()

        # bind lifecycle events
        self.bind("<<RouterAttached>>", self._router_attached)

    @property
    def outlet_name(self):
        return self._outlet_name

    # ---- router lifecycle (internal) ----
    def _router_attached(self, _: Any):
            self._render(self._router)

    def _router_navigated(self, route: Route, params: Dict[str, str]):
        self._render(self._router)

    def _render(self, router: Router | None):
        if not router:
            return
        match = router._match_route(router.path)
        if not match:
            return
        route, params = match
        self._mount_view(route, params)

    # ---- mounting / unmounting ----
    def _mount_view(self, route: Route, params: Dict[str, str]):
        # --- Unmount old view
        if self._active_view is not None:
            try:
                # Fire WILL UNMOUNT before we destroy, so listeners can react
                try:
                    self.emit(
                        event="route-will-unmount",
                        data=_payload(self._router.path if self._router else "", self._router.params if self._router else {}),
                        when="tail",
                    )
                except Exception:
                    pass
                if hasattr(self._active_view, "on_unmount"):
                    self._active_view.on_unmount()
            finally:
                old_root = getattr(self._active_view, "widget", self._active_view)
                try:
                    old_root.destroy()
                except Exception:
                    pass
                self._active_view = None

        # Safety: clear any remaining children in this outlet
        try:
            for child in list(self.widget.children.values()):
                try:
                    child.destroy()
                except Exception:
                    pass
        except Exception:
            pass

        # --- Construct new view inside our container context (parent optional)
        factory = route.view
        with self:
            try:
                # Prefer constructors that accept route params
                view = factory(**params)
            except TypeError:
                # Fallback to zero-arg constructor; parent resolves from context
                view = factory()

        self._active_view = view

        # --- Ensure the view itself is managed (mounted into *this* Pack) ---
        try:
            w = getattr(view, "widget", view)
            manager = w.winfo_manager() if hasattr(w, "winfo_manager") else ""
        except Exception:
            manager = ""

        if not manager:
            # Not managed yet: mount with defaults (or class defaults)
            pack_defaults = getattr(view, "pack_defaults", None)
            opts = pack_defaults if isinstance(pack_defaults, dict) else {"fill": "both", "expand": True}
            mounted = False

            # 1) Best: register directly with this outlet's Pack
            try:
                if hasattr(self, "add"):
                    self.add(view, **opts)   # ttkbootstrap.layouts.pack.Pack.add(...)
                    mounted = True
            except Exception:
                pass

            # 2) Next: lay out the view while this outlet is the active container
            if not mounted:
                try:
                    if hasattr(view, "layout"):
                        with self:
                            view.layout(**opts)
                        mounted = True
                except Exception:
                    pass

            # 3) Fallback: raw Tk pack on the underlying widget
            if not mounted:
                try:
                    w.pack(**opts)
                    mounted = True
                except Exception:
                    pass

            if not mounted:
                try:
                    self.emit(
                        event="<<RouteLayoutWarning>>",
                        data={"message": "RouterOutlet could not mount the view; check Pack.add/layout."},
                        when="tail",
                    )
                except Exception:
                    pass

        else:
            # Already managed: if it's pack with empty defaults, upgrade to full-page
            if manager == "pack":
                try:
                    info = w.pack_info() if hasattr(w, "pack_info") else {}
                except Exception:
                    info = {}

                fill = (info.get("fill") or "").strip()
                # pack_info may return '0'/'1' or int; normalize to int
                raw_expand = info.get("expand", 0)
                try:
                    expand = int(raw_expand)
                except Exception:
                    # Some Tk builds return booleans/strings; treat truthy as 1
                    expand = 1 if raw_expand in (True, "1", "true", "True") else 0

                # Only override the "empty defaults" that come from context auto-mounting
                if expand == 0 and (fill == "" or fill == "none"):
                    try:
                        if hasattr(view, "layout"):
                            with self:
                                view.layout(fill="both", expand=True)
                        else:
                            w.pack_configure(fill="both", expand=True)
                    except Exception:
                        # Last resort
                        try:
                            w.pack_configure(fill="both", expand=True)
                        except Exception:
                            pass
            else:
                # Conflicting geometry manager inside a Pack outlet
                try:
                    self.emit(
                        event="<<RouteLayoutWarning>>",
                        data={"message": f"View is managed by '{manager}' inside a Pack outlet; this may not be supported."},
                        when="tail",
                    )
                except Exception:
                    pass

        # Fire WILL MOUNT now that view exists but before final styling
        try:
            self.emit(
                event="<<RouteWillMount>>",
                data=_payload(self._router.path if self._router else "", params),
                when="tail",
            )
        except Exception:
            pass

        # Defer finalize so Tk can settle layout; then style refresh + on_mount
        if self._finalize_token:
            try:
                self.schedule_cancel(self._finalize_token)
            except Exception:
                pass
        self._finalize_token = self.schedule_after_idle(self._finalize_mount, view, params)

    def _finalize_mount(self, view, params: Dict[str, str]):
        self._finalize_token = None
        # Let Tk process geometry & pending draws
        try:
            self.widget.update_idletasks()
        except Exception:
            pass

        # Recursively re-apply ttkbootstrap styles where supported
        self._apply_style_recursive(view)

        try:
            self.widget.update_idletasks()
        except Exception:
            pass

        # on_mount after styles are stable
        if hasattr(view, "on_mount"):
            try:
                view.on_mount(params)
            except TypeError:
                try:
                    view.on_mount()
                except Exception:
                    pass

        # Fire DID MOUNT to signal routing is visually “done”
        try:
            self.emit(
                event="<<RouteDidMount>>",
                data=_payload(self._router.path if self._router else "", params),
                when="tail",
            )
        except Exception:
            pass

    # ---- style refresh ----
    def _apply_style_recursive(self, node):
        # Ask ttkbootstrap widgets/containers to re-apply theme style
        try:
            if hasattr(node, "update_style"):
                node.update_style()
        except Exception:
            pass

        # Collect children from ttkbootstrap containers and raw tk widgets
        kids = []
        try:
            kids += list(getattr(node, "children", {}).values())
        except Exception:
            pass
        try:
            w = getattr(node, "widget", node)
            kids += getattr(w, "winfo_children", lambda: [])()
        except Exception:
            pass

        seen = set()
        for c in kids:
            w = getattr(c, "widget", c)
            if w in seen:
                continue
            seen.add(w)
            self._apply_style_recursive(c)

    def _set_router(self):
        from ttkbootstrap.routing.navigation import get_router
        self._router = get_router()
        self._router.register_outlet(self)
        return self

    def navigate(self, path: str):
        if not self._router:
            raise RuntimeError("No router attached to this RouterOutlet.")
        self._router.navigate(path)
        return self
