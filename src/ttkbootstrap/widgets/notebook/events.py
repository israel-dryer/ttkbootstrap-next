from ttkbootstrap.types import BaseUIEvent
from ttkbootstrap.widgets.notebook.types import NotebookChangedData, TabLifecycleData

NotebookChangedEvent = BaseUIEvent[NotebookChangedData]
NotebookTabActivatedEvent = BaseUIEvent[TabLifecycleData]
NotebookTabDeactivatedEvent = BaseUIEvent[TabLifecycleData]
