from ttkbootstrap_next import App, Button, Pack, PageStack

with App("PageStack Demo") as app:
    with Pack().attach(fill='both', expand=True):
        with PageStack().attach(fill='both', expand=True) as s:
            with s.Pack("settings", surface="blue-200", fill_items='both', expand_items=True).attach() as tab1:
                Button('Go to Utilities', command=lambda: s.navigate('utilities')).attach()

            with s.Grid("utilities", surface="red-200", gap=8, padding=16, columns=1, rows=2, sticky_items="nsew").attach():
                Button('Go to Settings', command=lambda: s.navigate('settings')).attach()
                Button('Tab 2 - Option 2').attach()

        tab1.on_page_mounted().listen(lambda x: print(x))
        s.on_page_changed().listen(lambda x: print(x))

app.run()
