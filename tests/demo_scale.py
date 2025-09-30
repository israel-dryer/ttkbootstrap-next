from ttkbootstrap import App, Pack, Label, Scale
from ttkbootstrap.signals.signal import Signal

with App("Demo Scale") as app:
    # set signals
    scale_signal = Signal(40.2)
    label_signal = scale_signal.map(lambda x: str(round(x, 1)))

    with Pack(padding=16):
        scale = Scale(scale_signal, color="success", orient="vertical", precision=1).layout(fill="y", expand=True)
        Scale(value=0).on_changed().listen(lambda x: print(x))
        Label(label_signal)

app.run()
