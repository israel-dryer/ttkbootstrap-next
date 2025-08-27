from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.signals.signal import Signal
from ttkbootstrap.widgets import Label, Scale

with App("Demo Scale") as app:
    # set signals
    scale_signal = Signal(40.2)
    label_signal = scale_signal.map(lambda x: str(round(x, 1)))

    with Pack(padding=16):
        scale = Scale(scale_signal, color="success", orient="vertical", precision=1).layout(fill="y", expand=True)
        Label(label_signal)

app.run()
