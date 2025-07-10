from ttkbootstrap.style.builders.base import StyleBuilderBase


class EntryStyleBuilder(StyleBuilderBase):

    def __init__(self):
        super().__init__(f"TEntry")

    def register_style(self):
        ttk_style = self.resolve_name()
        self.configure(ttk_style, background=self.theme.color(self.surface()))
