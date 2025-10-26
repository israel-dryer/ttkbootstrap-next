from ttkbootstrap_next.types import UIEvent
from ttkbootstrap_next.widgets.notebook.types import NotebookChangedData, TabLifecycleData

NotebookChangedEvent = UIEvent[NotebookChangedData]
NotebookTabActivatedEvent = UIEvent[TabLifecycleData]
NotebookTabDeactivatedEvent = UIEvent[TabLifecycleData]
