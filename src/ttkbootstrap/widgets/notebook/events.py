from ttkbootstrap.types import UIEvent
from ttkbootstrap.widgets.notebook.types import NotebookChangedData, TabLifecycleData

NotebookChangedEvent = UIEvent[NotebookChangedData]
NotebookTabActivatedEvent = UIEvent[TabLifecycleData]
NotebookTabDeactivatedEvent = UIEvent[TabLifecycleData]
