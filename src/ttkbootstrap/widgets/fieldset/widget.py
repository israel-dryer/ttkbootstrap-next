from ttkbootstrap.events import Event
from ttkbootstrap.layouts.grid import Grid
from ttkbootstrap.layouts.layout_context import delegates_layout_context
from ttkbootstrap.layouts.pack import Pack
from ttkbootstrap.widgets.button import Button
from ttkbootstrap.widgets.label import Label


@delegates_layout_context('_body')
class Fieldset(Grid):
    """
    A titled group container with an optional description and a collapsible body.

    This widget composes a **header** (title/description and an optional chevron
    button) and a **body** that holds user content. Via the
    `@delegates_layout_context('_body')` decorator, the context manager delegates
    to the internal body container so children auto-mount into the body:

        with Fieldset("Advanced", collapsible=True, expanded=False) as fs:
            # children are placed in fs.body automatically
            ...

    Events
    ------
    - Emits `Event.GROUP_TOGGLED` (aka `<<GroupToggled>>`) when the expanded
      state is toggled, with an `expanded: bool` payload.
    """

    _body: Pack

    def __init__(self, title: str, description: str = None, collapsible=False, expanded=True, **kwargs):
        """
        Create a new Fieldset.

        Parameters
        ----------
        title:
            The header title text shown at the top of the fieldset.
        description:
            Optional secondary text shown under the title; hidden when falsy.
        collapsible:
            If `True`, a chevron button is shown in the header and the body can
            be shown/hidden. If `False`, the chevron is hidden and the body
            remains visible.
        expanded:
            Initial expansion state. If `False`, the body starts hidden and the
            chevron points right (LTR).
        **kwargs:
            Forwarded to `Grid` (e.g., `padding`, `width`, `height`, `surface`,
            etc.). The Fieldset itself is a 1×2 grid: row 0 is the header,
            row 1 is the body.

        Structure & Behavior
        --------------------
        - Header (row 0): a small internal `Grid` with two columns:
            * col 0: a vertical `Pack` containing the title and description
            * col 1: an optional chevron `Button` (shown when `collapsible=True`)
        - Body (row 1): a `Pack` that serves as the content container and the
          layout context target. Children created inside the `with Fieldset():`
          block auto-mount into this body.
        - Initial state mirrors `collapsible` and `expanded`, hiding the chevron
          and/or the body as needed.
        """
        self._title = title
        self._description = description
        self._collapsible = collapsible
        self._expanded = expanded

        super().__init__(columns=1, rows=[0, 1], **kwargs)
        self._initialize_widget()

    def _initialize_widget(self):
        """Build the header (title/description/chevron) and body containers."""
        # header container
        with Grid(parent=self, rows=1, columns=[1, 0], padding=(8, 4)) as self._header:
            self._header.attach(column=0, row=0, sticky="ew")

            # header text container
            with Pack(direction="vertical") as self._header_text_container:
                self._header_text_container.layout(sticky="w", column=0, row=0)
                self._title_widget = Label(self._title, font="heading-md", anchor="w").layout(fill="x")
                self._description_widget = Label(self._description, anchor="w")

            # toggle button
            self._toggle_btn = Button(
                padding=8,
                variant="list",
                take_focus=False,
                icon="chevron-down" if self._expanded else "chevron-right",
            )
            self._toggle_btn.on_invoke(self.toggle)
            self._toggle_btn.layout(column=1, row=0)

        # body container
        self._body = Pack(parent=self).attach(sticky="nsew", column=0, row=1)

        # set initial state
        if not self._collapsible:
            self._toggle_btn.hide()

        if not self._expanded:
            self._body.hide()

        if not self._description:
            self._description_widget.hide()

    @property
    def body(self):
        """Return the inner content container (`Pack`) for advanced usage."""
        return self._body

    def title(self, value: str = None):
        """Get or set the title text; updates the header label when set (chainable)."""
        if value is None:
            return self._title
        else:
            self._title = value
            self._title_widget.text(value)
        return self

    def description(self, value: str = None):
        """Get or set the description text; hides the label when falsy (chainable)."""
        if value is None:
            return self._description
        else:
            self._description = value
            self._description_widget.text(value)
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
                self.body.attach()
            else:
                self.body.hide()
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
            self._body.hide()
            self._toggle_btn.icon("chevron-right")
        else:
            self._body.attach()
            self._toggle_btn.icon("chevron-down")

        # Notify listeners (payload reflects the state before flipping)
        self.emit(Event.GROUP_TOGGLED, expanded=self._expanded)

        # Flip expansion state
        self._expanded = not self._expanded
