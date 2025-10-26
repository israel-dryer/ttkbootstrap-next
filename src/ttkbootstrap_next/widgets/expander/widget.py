from typing import Literal, Unpack, cast

from ttkbootstrap_next.events import Event
from ttkbootstrap_next.layouts.grid import Grid
from ttkbootstrap_next.layouts.pack import Pack
from ttkbootstrap_next.layouts.types import GridOptions
from ttkbootstrap_next.utils import tag_descendents
from ttkbootstrap_next.widgets.button import Button
from ttkbootstrap_next.widgets.label import Label
from ttkbootstrap_next.widgets.mixins.composite_mixin import CompositeWidgetMixin

DEFAULT_EXPANDER_OPEN_ICON = {"name": "chevron-up", "size": 12}
DEFAULT_EXPANDER_CLOSED_ICON = {"name": "chevron-down", "size": 12}
DEFAULT_EXPANDER_POSITION = 'after'


class ExpanderOptions(GridOptions, total=False):
    """Accepts layout options passed to the grid container, as well as select expander button attributes.

        Attributes:
            open_icon: A dictionary of icon options [name, size]
            closed_icon: A dictionary of icon options [name, size]
            button_position: Where to place the button relative to the header content. Default is 'after'.
    """
    open_icon: dict
    closed_icon: dict
    button_position: Literal['before', 'after']


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
            self, title: str, collapsible=True, expanded=True,
            **kwargs: Unpack[ExpanderOptions]):
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
        **kwargs:
            Expander button options for expander button icon and position. Also,
            layout options that are forwarded to `Grid` (e.g., `padding`, `width`,
            `height`, `surface`, etc.). The Fieldset itself is a 1×2 grid: row 0
            is the header, row 1 is the body.
        """
        self._title = title
        self._collapsible = collapsible
        self._expanded = expanded

        # set expander button properties
        opts = cast(dict, kwargs)
        self._open_icon = opts.pop('open_icon', DEFAULT_EXPANDER_OPEN_ICON)
        self._closed_icon = opts.pop('closed_icon', DEFAULT_EXPANDER_CLOSED_ICON)
        self._button_position = opts.pop('button_position', DEFAULT_EXPANDER_POSITION)
        self._customize_header = False

        super().__init__(columns=1, rows=[0, 1], padding=1, **kwargs)
        self._initialize_widget()

    @property
    def _current_expander_icon(self):
        return self._open_icon if self._expanded else self._closed_icon

    @property
    def _header_column_weights(self):
        if self._button_position == 'after':
            return [1, 0]
        else:
            return [0, 1]

    def _initialize_widget(self):
        """Build the header (title/chevron) and content containers."""
        # widget layout
        cols = self._header_column_weights
        with self:
            # header container
            with Grid(rows=1, columns=cols, padding=4).attach() as self._header:
                self._header.attach(column=0, row=0, sticky="ew")

                # header text container
                with Pack(direction="horizontal").attach() as self._header_text_container:
                    self._header_text_container.attach(sticky="ew", column=cols[1], row=0)
                    self._title_widget = Label(self._title, anchor="w", padding=(4, 0)).attach(fill="x")

                # toggle button
                self._toggle_btn = Button(
                    padding=8, variant="ghost", color="foreground",
                    icon=self._current_expander_icon)
                self._toggle_btn.attach(column=cols[0], row=0)
                self._toggle_btn.on(Event.KEYUP_SPACE).listen(lambda x: self.toggle())

            # content container
            self._content = Pack(padding=16).attach(sticky="nsew", column=0, row=1)

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
            self._title_widget.configure(text=value)
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
        self._toggle_btn.configure(icon=self._current_expander_icon)

        # Notify listeners (payload reflects the state before flipping)
        self.emit(Event.GROUP_TOGGLED, expanded=self._expanded)

    def _bind_header_tags(self):
        """Bind the header and descendent widgets for toggle event."""
        tag = str(self._header.widget.winfo_id()) + '_header'
        tag_descendents(self._header, tag)
        self._header.on(Event.CLICK1, scope=tag).listen(lambda *_: self.toggle())
