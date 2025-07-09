from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.style import Style


class ScrollbarStyleBuilder(StyleBuilderBase):

    def __init__(self, orient="vertical"):
        super().__init__(f"TScrollbar", orient=orient)

    def orient(self, value=None):
        if value is None:
            return self.options.get('orient') or 'vertical'
        else:
            self.options.update(orient=value)
            return self

    def register_style(self):
        ttk_style = self.resolve_name()
        style = Style()
        layout = style.layout(f"{self.orient().title()}.TScrollbar")
        style.layout(ttk_style, layout)
        self.configure(ttk_style)
