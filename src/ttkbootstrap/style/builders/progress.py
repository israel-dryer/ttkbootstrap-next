from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.style import Style


class ProgressStyleBuilder(StyleBuilderBase):

    def __init__(self, orient="horizontal"):
        super().__init__(f"TProgressbar", orient=orient)

    def orient(self, value=None):
        if value is None:
            return self.options.get('orient') or 'horizontal'
        else:
            self.options.update(orient=value)
            return self

    def register_style(self):
        ttk_style = self.resolve_name()
        style = Style()
        layout = style.layout(f"{self.orient().title()}.TProgressbar")
        style.layout(ttk_style, layout)
        self.configure(ttk_style)
