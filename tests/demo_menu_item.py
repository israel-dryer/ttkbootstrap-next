from ttkbootstrap import App, Pack
from ttkbootstrap.widgets.menu.menu_item import MenuItem

with App() as app:
    with Pack(fill_items='x').attach(fill='x'):
        MenuItem("New Project...").attach()
        MenuItem("Project from Version Control...").attach()
        MenuItem("New...", underline=0, shortcut_text="Alt+Insert").attach()
        MenuItem("New Scratch File", shortcut_text="Ctrl+Alt+Shift+Insert").attach()
        MenuItem("Open...", icon="folder", underline=0).attach()
        MenuItem("Save As...").attach()
        MenuItem("Recent Projects", item_type="cascade", underline=0).attach()
        MenuItem("Close Project").attach()
        MenuItem("Rename Project...").attach()
        MenuItem("Remote Development...", begin_group=True).attach()
        MenuItem("Settings...", icon="gear", underline=2, shortcut_text="Ctrl+Alt+S", begin_group=True).attach()
        MenuItem("File Properties", item_type="cascade").attach()
        MenuItem("Local History", begin_group=True, underline=6).attach()
        MenuItem("Save All", underline=0, icon="floppy", shortcut_text="Ctrl+S").attach()
        MenuItem("Reload All from Disk", icon="arrow-clockwise", shortcut_text="Ctrl+Alt+Y").attach()
        MenuItem("Repair IDE").attach()
        MenuItem("Invalidate Caches...").attach()
        MenuItem("Manage IDE Settings", begin_group=True, item_type="cascade").attach()
        MenuItem("New Projects Setup", item_type="cascade").attach()
        MenuItem("Save File as Template...").attach()
        MenuItem("Export", begin_group=True).attach()
        MenuItem("Print...", underline=0, icon="printer").attach()
        MenuItem("Power Save Mode", begin_group=True).attach()
        MenuItem("Exit", underline=1, begin_group=True).attach()

app.run()
