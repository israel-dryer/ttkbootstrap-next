from ttkbootstrap.types import UIEvent
from ttkbootstrap.widgets.entry.types import (
    EntryChangedData, EntryEnterData, EntryInputData,
    SpinboxChangedData, SpinboxEnterData, SpinboxInputData
)

SpinboxChangedEvent = UIEvent[SpinboxChangedData]
SpinboxEnterEvent = UIEvent[SpinboxEnterData]
SpinboxInputEvent = UIEvent[SpinboxInputData]
EntryChangedEvent = UIEvent[EntryChangedData]
EntryEnterEvent = UIEvent[EntryEnterData]
EntryInputEvent = UIEvent[EntryInputData]
