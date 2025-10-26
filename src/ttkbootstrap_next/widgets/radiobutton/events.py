from ttkbootstrap_next.types import UIEvent
from ttkbootstrap_next.widgets.radiobutton.types import RadiobuttonChangedData, RadiobuttonInvokeData

RadiobuttonSelectedEvent = UIEvent[RadiobuttonChangedData]
RadiobuttonDeselectedEvent = UIEvent[RadiobuttonChangedData]
RadiobuttonInvokeEvent = UIEvent[RadiobuttonInvokeData]
