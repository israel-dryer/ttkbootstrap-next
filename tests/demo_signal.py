import tkinter as tk
from ttkbootstrap.core.signal import Signal  # Replace with actual path or relative import

def main():
    root = tk.Tk()
    root.title("Signal Demo")
    root.geometry("300x200")

    # Create a signal for the text input
    name_signal = Signal("world")

    # Create a derived signal that transforms the value to uppercase
    upper_signal = name_signal.map(lambda val: val.upper())

    # Entry widget bound to the signal's variable
    entry = tk.Entry(root, textvariable=name_signal.name)
    entry.pack(pady=10)

    # Label that reacts to updates from the signal
    label = tk.Label(root)
    label.pack(pady=10)

    # Another label that shows the mapped uppercase version
    upper_label = tk.Label(root, fg="blue")
    upper_label.pack(pady=10)

    # Reactively update the label when the signal changes
    name_signal.subscribe(lambda val: label.config(text=f"Hello, {val}!"))
    upper_signal.subscribe(lambda val: upper_label.config(text=f"Upper: {val}"))

    root.mainloop()

if __name__ == "__main__":
    main()
