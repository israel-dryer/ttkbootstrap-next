from typing import Optional, Union, Unpack

from ttkbootstrap.layouts import Grid, Pack
from ttkbootstrap.types import Widget
from ttkbootstrap.widgets.notebook.types import GridTabOptions, PackTabOptions


class TabMixin:
    """Mixin that adds tab metadata and tab-specific options."""
    widget: Widget

    def __init__(self, **kwargs):
        # Stable developer key (optional; Notebook will auto-generate if missing)
        self._tab_key: Optional[str] = kwargs.pop('key', None)

        # Keep ttk tab options for .add()
        self._tab_options = {}
        for k in ['underline', 'state', 'sticky', 'image', 'compound', 'text']:
            if k in kwargs:
                self._tab_options[k] = kwargs.pop(k)

        super().__init__(**kwargs)

    @property
    def key(self) -> Optional[str]:
        """Stable developer key for this tab (if provided)."""
        return self._tab_key


class TabGrid(TabMixin, Grid):
    def __init__(self, text: str = "", *, key: str | None = None, **kwargs: Unpack[GridTabOptions]):
        super().__init__(text=text, key=key, **kwargs)


class TabPack(TabMixin, Pack):
    def __init__(self, text: str = "", *, key: str | None = None, **kwargs: Unpack[PackTabOptions]):
        super().__init__(text=text, key=key, **kwargs)


Tab = Union[str, int, TabGrid, TabPack]
