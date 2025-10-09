from ttkbootstrap.types import UIEvent
from ttkbootstrap.widgets.entry.types import (
    EntryChangedEventData, EntryEnterEventData, EntryInputEventData,
    SpinboxChangedEventData, SpinboxEnterEventData, SpinboxInputEventData
)

SpinboxChangedEvent = UIEvent[SpinboxChangedEventData]
SpinboxEnterEvent = UIEvent[SpinboxEnterEventData]
SpinboxInputEvent = UIEvent[SpinboxInputEventData]
EntryChangedEvent = UIEvent[EntryChangedEventData]
EntryEnterEvent = UIEvent[EntryEnterEventData]
EntryInputEvent = UIEvent[EntryInputEventData]
