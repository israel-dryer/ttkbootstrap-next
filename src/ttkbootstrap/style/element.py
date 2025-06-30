from tkinter import ttk
from typing import Optional, Union, List, Tuple, Iterable, Any

from ..core.image import ManagedImage


class Element:
    def __init__(
            self,
            name: str,
            *,
            expand: Optional[bool] = None,
            side: Optional[str] = None,
            sticky: Optional[str] = None,
            border: Optional[int] = None,
    ):
        self.name = name
        self.parent: Optional[Element] = None
        self._children: list[Element] = []
        self._options: dict[str, Any] = {
            "expand": expand,
            "side": side,
            "sticky": sticky,
            "border": border,
        }

    @property
    def children(self) -> List["Element"]:
        return self._children

    def add_parent(self, parent: "Element") -> None:
        self.parent = parent
        parent._children.append(self)

    def layout(self, layout: Iterable["Element"], style: ttk.Style) -> None:
        def assign_parents(elements: Iterable[Any], parent: Optional[Element] = None):
            for i, item in enumerate(elements):
                if isinstance(item, Element) and parent:
                    item.add_parent(parent)
                elif isinstance(item, (list, tuple)):
                    assign_parents(item, elements[i - 1] if i > 0 else None)

        assign_parents(layout, self)
        layout_script = self._to_script()
        style.tk.call("ttk::style", "layout", self.name, layout_script)

    def _to_script(self) -> str:
        return f"{{{self._element_script(self)}}}"

    def _element_script(self, root: "Element") -> str:
        tokens = [self.name]
        for k, v in self._options.items():
            if v is not None:
                tokens.extend([f"-{k}", str(v).lower()])

        if self.children:
            tokens.append("-children")
            children_scripts = [child._element_script(root) for child in self.children]
            tokens.append(f"{{{''.join(f'{{{cs}}}' for cs in children_scripts)}}}")
        return " ".join(tokens)


class ElementImage:
    def __init__(
            self,
            name: str,
            image: Union[str, ManagedImage],
            *,
            border: Optional[Union[int, Tuple[int, int]]] = None,
            height: Optional[int] = None,
            width: Optional[int] = None,
            padding: Optional[Union[int, Tuple[int, ...]]] = None,
            sticky: Optional[str] = None,
    ):
        self._name = name
        self._image = image
        self._image_specs: list[tuple[str, Union[str, ManagedImage]]] = []
        self._options: dict[str, Any] = {
            "border": border,
            "height": height,
            "width": width,
            "padding": padding,
            "sticky": sticky,
        }

    @property
    def name(self) -> str:
        return self._name

    def add_spec(self, state: str, image: Union[str, ManagedImage]) -> None:
        self._image_specs.append((state, image))

    def build(self, style: ttk.Style) -> None:
        image_list = [str(self._image)]
        for state, img in self._image_specs:
            image_list.append(f"{{{state}}}")
            image_list.append(str(img))

        # Wrap in Tcl-style [list ...]
        image_spec = style.tk.call("list", *image_list)

        option_list = []
        for k, v in self._options.items():
            if v is not None:
                val = " ".join(map(str, v)) if isinstance(v, (list, tuple)) else str(v)
                option_list.extend(["-" + k, f"{{{val}}}"])

        style.tk.call(
            "ttk::style", "element", "create", self._name, "image", image_spec, *option_list
        )

    def state_specs(self, specs: list[Tuple[str, Union[str, ManagedImage]]]):
        for spec in specs:
            self.add_spec(*spec)
        return self

    def __str__(self) -> str:
        return self.name

    def __call__(self, *specs: Tuple[str, Union[str, ManagedImage]]):
        for spec in specs:
            self.add_spec(*spec)
        return self
