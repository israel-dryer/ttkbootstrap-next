from ttkbootstrap.layouts import Pack
from ttkbootstrap.routing import Router


class RouterOutlet(Pack):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._router: Router | None = None
        self._active_view = None
        self._finalize_token = None

    # ---- router lifecycle (internal) ----

    def _router_attached(self, router):
        self._router = router
        self._render(router)

    def _router_navigated(self):
        self._render(self._router)

    def _render(self, router: Router | None):
        if not router:
            return
