from ttkbootstrap.core import App
from ttkbootstrap.widgets import Button, Frame
from ttkbootstrap.widgets.mixins import CompositeWidgetMixin


class TestCombined(Frame, CompositeWidgetMixin):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self._inner_frame = Frame(self, padding=16).pack()

        self._button = Button(self._inner_frame, text="Push")
        self._button.pack()
        self.register_composite_widgets([self._inner_frame, self._button])


if __name__ == '__main__':

    app = App()

    TestCombined(app, padding=32).pack()

    app.run()

