from ttkbootstrap import App, Pack, Label, Scale
from ttkbootstrap.signals.signal import Signal

with App("Demo Scale") as app:
    # set signals
    scale_signal = Signal(40.2)
    label_signal = scale_signal.map(lambda x: str(round(x, 1)))

    with Pack(padding=16).attach():
        s = scale = Scale(scale_signal, color="success", orient="vertical", precision=1).attach(fill="y", expand=True)
        s.configure(color="danger")
        Scale(value=0).attach().on_changed().listen(lambda x: print(x))
        Label(label_signal).attach()

app.run()
