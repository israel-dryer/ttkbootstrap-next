from ttkbootstrap.types import UIEvent
from ttkbootstrap.widgets.entry.types import SpinboxChangedData, SpinboxEnterData, SpinboxInputData

SpinboxChangedEvent = UIEvent[SpinboxChangedData]
SpinboxEnterEvent = UIEvent[SpinboxEnterData]
SpinboxInputEvent = UIEvent[SpinboxInputData]
