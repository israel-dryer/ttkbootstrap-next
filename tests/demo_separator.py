from ttkbootstrap import App, Pack, Separator

with App("Separator Demo", geometry="400x400") as app:
    with Pack(gap=16, direction="vertical", padding=16).layout(fill='x'):
        Separator(color="danger").layout(fill='x', expand=True)
        Separator().layout(fill='x', expand=True)
app.run()