from ttkbootstrap import App, Pack, Badge

with App(theme="light") as app:
    with Pack(padding=16, gap=8).attach(fill="both", expand=True):
        Badge("21+").attach()
        Badge("2", variant="circle").attach()
        Badge("355 lbs", variant="pill").attach()
app.run()
