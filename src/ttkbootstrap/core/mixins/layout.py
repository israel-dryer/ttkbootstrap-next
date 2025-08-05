from typing import TYPE_CHECKING, Any

from ttkbootstrap.core.libtypes import Margin, LayoutMethod, SemanticLayoutOptions

if TYPE_CHECKING:
    from ttkbootstrap.core.widget import BaseWidget


class LayoutMixin:
    """
    A mixin that provides layout abstraction for widgets across Tkinter's
    geometry managers (`pack`, `grid`, and `place`).

    This mixin handles the parsing of high-level semantic layout options
    (e.g., `justify`, `align`, `margin`, `expand`) and translates them into
    low-level Tkinter layout arguments. It supports declarative layout
    configuration and enables consistent layout behavior across different
    geometry managers.

    Attributes:
        widget (BaseWidget): The widget to which the layout will be applied.
        _layout_options (dict): Parsed semantic layout configuration stored at initialization.
    """

    widget: "BaseWidget"

    def __init__(self, layout: dict = None, **kwargs):
        """
        Initialize the LayoutMixin with semantic layout options.

        Args:
            layout: A dictionary of semantic layout options. This is typically
                    extracted from widget keyword arguments using `layout_from_options`.
            **kwargs: (Unused) for compatibility with flexible subclassing.
        """
        self._layout_options = layout or {}

    def mount(self, method: LayoutMethod = "pack", **kwargs):
        """
        Mount the widget using the given geometry manager and apply translated layout options.

        Args:
            method: The layout method to use ("pack", "grid", or "place").
            **kwargs: Any additional or overriding keyword arguments passed to the geometry manager.
        """
        method = method.lower()

        # Merge translated layout options with any overrides
        layout_opts = self._translate_layout(method)

        # Strip semantic-only options that don't belong in the geometry call
        for key in ("justify", "align", "margin"):
            layout_opts.pop(key, None)

        # Final layout configuration
        opts = {**layout_opts, **kwargs}

        # Apply geometry manager
        match method:
            case "pack":
                self.widget.pack(**opts)
            case "grid":
                self.widget.grid(**opts)
            case "place":
                self.widget.place(**opts)

    @staticmethod
    def layout_from_options(kwargs: dict[str, Any]) -> SemanticLayoutOptions:
        """
        Extract semantic layout options from a widget constructor's keyword arguments.

        This mutates the original dictionary by removing layout-related keys.

        Args:
            kwargs: The keyword argument dictionary to extract from.

        Returns:
            A dict containing only recognized layout-related options.
        """
        layout: SemanticLayoutOptions = {}
        for key in list(SemanticLayoutOptions.__annotations__.keys()):
            if key in kwargs:
                layout[key] = kwargs.pop(key)
        return layout

    def _translate_layout(self, method: str) -> dict:
        """
        Dispatch layout translation based on the geometry manager.

        Args:
            method: The geometry manager being used ("pack", "grid", or "place").

        Returns:
            A dictionary of options compatible with the specified layout method.
        """
        layout = self._layout_options.copy()

        match method:
            case "pack":
                return self._translate_pack_layout(layout)
            case "grid":
                return self._translate_grid_layout(layout)
            case "place":
                return self._translate_place_layout(layout)
            case _:
                return {}

    @staticmethod
    def _translate_margin(margin: Margin) -> dict:
        """
        Convert semantic margin definition into `padx` and `pady` options.

        Args:
            margin: The margin value (int or tuple of 2 or 4 ints).

        Returns:
            A dictionary with `padx` and `pady` keys.
        """
        if isinstance(margin, int):
            return {"padx": margin, "pady": margin}
        elif isinstance(margin, tuple) and len(margin) == 2:
            return {"padx": margin[0], "pady": margin[1]}
        elif isinstance(margin, tuple) and len(margin) == 4:
            return {
                "padx": (margin[3], margin[1]),  # left, right
                "pady": (margin[0], margin[2])  # top, bottom
            }
        return {}

    def _translate_pack_layout(self, layout: dict) -> dict:
        """
        Translate semantic layout options to `pack` geometry arguments.

        Args:
            layout: The parsed layout options.

        Returns:
            A dictionary of `pack()`-compatible options.
        """
        opts = self._translate_margin(layout.get("margin", 0))
        justify = layout.get("justify", "left")
        align = layout.get("align", "top")

        opts["expand"] = layout.get("expand", False)
        opts["side"] = layout.get("side") or {
            "left": "left",
            "center": "top",
            "right": "right",
            "stretch": "top"
        }.get(justify, "left")

        if justify == "stretch" and align == "stretch":
            opts["fill"] = "both"
        elif justify == "stretch":
            opts["fill"] = "x"
        elif align == "stretch":
            opts["fill"] = "y"

        if align == "center":
            opts["anchor"] = "center"
        elif align == "top":
            opts["anchor"] = "n"
        elif align == "bottom":
            opts["anchor"] = "s"

        return opts

    def _translate_grid_layout(self, layout: dict) -> dict:
        """
        Translate semantic layout options to `grid` geometry arguments.

        Args:
            layout: The parsed layout options.

        Returns:
            A dictionary of `grid()`-compatible options.
        """
        opts = self._translate_margin(layout.get("margin", 0))
        justify = layout.get("justify", "left")
        align = layout.get("align", "top")

        sticky = ""
        sticky += {
            "left": "w", "center": "", "right": "e", "stretch": "ew"
        }.get(justify, "")
        sticky += {
            "top": "n", "center": "", "bottom": "s", "stretch": "ns"
        }.get(align, "")
        opts["sticky"] = "".join(sorted(set(sticky)))

        for key in ("row", "column", "rowspan", "colspan"):
            if key in layout:
                opts["columnspan" if key == "colspan" else key] = layout[key]

        return opts

    @staticmethod
    def _translate_place_layout(layout: dict) -> dict:
        """
        Translate semantic layout options to `place` geometry arguments.

        Args:
            layout: The parsed layout options.

        Returns:
            A dictionary of `place()`-compatible options.
        """
        return {
            key: layout[key]
            for key in (
                "x", "y", "relx", "rely", "anchor",
                "width", "height", "relwidth", "relheight"
            )
            if key in layout
        }
