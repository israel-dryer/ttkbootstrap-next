from ttkbootstrap.types import UIEvent
from ttkbootstrap.widgets.radiobutton.types import RadiobuttonChangedData, RadiobuttonInvokeData

RadiobuttonSelectedEvent = UIEvent[RadiobuttonChangedData]
RadiobuttonDeselectedEvent = UIEvent[RadiobuttonChangedData]
RadiobuttonInvokeEvent = UIEvent[RadiobuttonInvokeData]
