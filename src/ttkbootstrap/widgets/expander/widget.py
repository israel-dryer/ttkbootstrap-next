from ttkbootstrap.events import Event
from ttkbootstrap.layouts.grid import Grid
from ttkbootstrap.layouts.pack import Pack
from ttkbootstrap.utils import tag_descendents
from ttkbootstrap.widgets.label import Label
from ttkbootstrap.widgets.mixins.composite_mixin import CompositeWidgetMixin

DEFAULT_EXPANSION_ICONS = {
    "open": {"name": "chevron-up", "size": 12},
    "closed": {"name": "chevron-down", "size": 12}
}


class _HeaderProxy:
    """Wraps the header text container to optionally clear the defaults on first use"""

    def __init__(self, expander: "Expander"):
        self._expander = expander

    def __enter__(self):
        expander = self._expander
        if getattr(expander, "_customize_header", False):
            return
        setattr(expander, "_customize_header", True)

        # remove default title widget
        getattr(expander, "_title_widget").destroy()

        # return real header so automount works
        header = getattr(expander, "_header_text_container")
        return header.__enter__()

    def __exit__(self, *args):
        header = getattr(self._expander, "_header_text_container")
        header.__exit__(*args)

    def __getattr__(self, name):
        header = getattr(self._expander, "_header_text_container")
        return getattr(header, name)


class Expander(Grid, CompositeWidgetMixin):
    """
    A titled group container with a collapsible body.

    This widget composes a **header** (title/description and an optional chevron
    button) and **content** that holds user content.

    Events
    ------
    - Emits `Event.EXPANDED` (aka `<<Expanded>>`) when the expanded
      state is toggled, with an `expanded: bool` payload.
    """

    _content: Pack

    def __init__(
            self, title: str, *, collapsible=True, expanded=True,
            expander_icon: dict[str, str] = None, **kwargs):
        """
        Create a new Fieldset.

        Parameters
        ----------
        title:
            The header title text shown at the top of the fieldset.
        collapsible:
            If `True`, a chevron button is shown in the header and the body can
            be shown/hidden. If `False`, the chevron is hidden and the body
            remains visible.
        expanded:
            Initial expansion state. If `False`, the widget starts closed..
        expander_icon:
            The icon set to show when the expander is open or close. A dictionary
            of icon values {"open": "minus", "closed": "plus"}.
        **kwargs:
            Forwarded to `Grid` (e.g., `padding`, `width`, `height`, `surface`,
            etc.). The Fieldset itself is a 1×2 grid: row 0 is the header,
            row 1 is the body.
        """
        self._title = title
        self._collapsible = collapsible
        self._expanded = expanded
        self._expander_icon = expander_icon or DEFAULT_EXPANSION_ICONS
        self._customize_header = False

        super().__init__(columns=1, rows=[0, 1], padding=1, **kwargs)
        self._initialize_widget()

    def _current_expander_icon(self):
        state = "open" if self._expanded else "closed"
        return self._expander_icon[state]

    def _initialize_widget(self):
        """Build the header (title/chevron) and content containers."""
        # widget layout
        with self:
            # header container
            with Grid(rows=1, columns=[1, 0], padding=8) as self._header:
                self._header.layout(column=0, row=0, sticky="ew")

                # header text container
                with Pack(direction="horizontal") as self._header_text_container:
                    self._header_text_container.layout(sticky="ew", column=0, row=0)
                    self._title_widget = Label(self._title, anchor="w", padding=(4, 0)).layout(fill="x")

                # toggle button
                self._toggle_btn = Label(
                    padding=8, variant="text", take_focus=False,
                    icon=self._current_expander_icon()
                )
                # self._toggle_btn.on(Event.CLICK1).listen(lambda *_: self.toggle())
                self._toggle_btn.layout(column=1, row=0)

            # content container
            self._content = Pack(padding=16).layout(sticky="nsew", column=0, row=1)

        # set initial state
        if not self._collapsible:
            self._toggle_btn.hide()
        else:
            self._bind_header_tags()

        if not self._expanded:
            self._content.hide()

    @property
    def header(self):
        """Return the inner header container (`Pack`) for advanced usage"""
        return _HeaderProxy(self)

    @property
    def content(self):
        """Return the inner content container (`Pack`) for advanced usage."""
        return self._content

    def title(self, value: str = None):
        """Get or set the title text; updates the header label when set (chainable)."""
        if value is None:
            return self._title
        else:
            self._title = value
            self._title_widget.text(value)
        return self

    def collapsible(self, value: bool = None):
        """
        Get or set whether the fieldset is collapsible (chainable).

        Note: This setter controls visibility of the body in this implementation
        (`True` → body shown, `False` → body hidden). It does not recreate or
        remove the header chevron button at runtime; the affordance is decided
        during `__init__`.
        """
        if value is None:
            return self._collapsible
        else:
            self._collapsible = value
            if value:
                self.content.attach()
            else:
                self.content.hide()
            return self

    def toggle(self):
        """
        Toggle the expanded/collapsed state.

        Updates the body visibility and chevron icon, and emits
        `Event.GROUP_TOGGLED` with an `expanded: bool` payload reflecting the
        current state at the time of emission.
        """
        # Set body and button state
        if self._expanded:
            self._content.hide()
        else:
            self._content.attach()

        # Flip expansion state
        self._expanded = not self._expanded
        self._toggle_btn.icon(self._current_expander_icon())

        # Notify listeners (payload reflects the state before flipping)
        self.emit(Event.GROUP_TOGGLED, expanded=self._expanded)

    def _bind_header_tags(self):
        """Bind the header and descendent widgets for toggle event."""
        tag = str(self._header.widget.winfo_id()) + '_header'
        tag_descendents(self._header, tag)
        self._header.on(Event.CLICK1, scope=tag).listen(lambda *_: self.toggle())
