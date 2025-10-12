from ttkbootstrap import App, Pack, Badge

with App() as app:
    with Pack(padding=16, gap=8).attach():
        Badge("21+").attach()
        Badge("2", variant="circle").attach()
        Badge("355 lbs", variant="pill").attach()
app.run()
