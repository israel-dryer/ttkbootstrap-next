from ttkbootstrap import App, Pack, Button, PageStack

with App("PageStack Demo") as app:
    with Pack().layout(fill='both', expand=True):
        with PageStack().layout(fill='both', expand=True) as s:
            with s.Pack("settings", surface="blue-200", fill_items='both', expand_items=True) as tab1:
                Button('Go to Utilities', on_invoke=lambda: s.navigate('utilities'))

            with s.Grid("utilities", surface="red-200", gap=8, padding=16, columns=1, rows=2, sticky_items="nsew"):
                Button('Go to Settings', on_invoke=lambda: s.navigate('settings'))
                Button('Tab 2 - Option 2')

        tab1.on_page_mounted(lambda x: print(x))
        s.on_page_changed(lambda x: print(x))

app.run()
