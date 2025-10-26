from ttkbootstrap_next import App, Pack
from ttkbootstrap_next.widgets.menu.menu_item import MenuItem

with App() as app:
    with Pack(fill_items='x').attach(fill='x'):
        MenuItem(label="New Project...").attach()
        MenuItem(label="Project from Version Control...").attach()
        MenuItem(label="New...", underline=0, accelerator="Alt+Insert").attach()
        MenuItem(label="New Scratch File", accelerator="Ctrl+Alt+Shift+Insert").attach()
        MenuItem(label="Open...", icon="folder", underline=0).attach()
        MenuItem(label="Save As...").attach()
        MenuItem(label="Recent Projects", item_type="cascade", underline=0).attach()
        MenuItem(label="Close Project").attach()
        MenuItem(label="Rename Project...").attach()
        MenuItem(label="Remote Development...", begin_group=True).attach()
        MenuItem(label="Settings...", icon="gear", underline=2, accelerator="Ctrl+Alt+S", begin_group=True).attach()
        MenuItem(label="File Properties", item_type="cascade").attach()
        MenuItem(label="Local History", begin_group=True, underline=6).attach()
        MenuItem(label="Save All", underline=0, icon="floppy", accelerator="Ctrl+S").attach()
        MenuItem(label="Reload All from Disk", icon="arrow-clockwise", accelerator="Ctrl+Alt+Y").attach()
        MenuItem(label="Repair IDE").attach()
        MenuItem(label="Invalidate Caches...").attach()
        MenuItem(label="Manage IDE Settings", begin_group=True, item_type="cascade").attach()
        MenuItem(label="New Projects Setup", item_type="cascade").attach()
        MenuItem(label="Save File as Template...").attach()
        MenuItem(label="Export", begin_group=True).attach()
        MenuItem(label="Print...", underline=0, icon="printer").attach()
        MenuItem(label="Power Save Mode", begin_group=True).attach()
        MenuItem(label="Exit", underline=1, begin_group=True).attach()

app.run()
