from ttkbootstrap_next import App, Pack, Separator

with App("Separator Demo", geometry="400x400") as app:
    with Pack(gap=16, direction="vertical", padding=16).attach(fill='x'):
        Separator(color="danger").attach(fill='x', expand=True)
        Separator().attach(fill='x', expand=True)
app.run()
