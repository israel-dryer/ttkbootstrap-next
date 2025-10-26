"""Test to verify if the event system works with drag events."""
import sys
import os

# Fix encoding for Windows console
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

# Add src directory to path
sys.path.insert(0, r'D:\Development\ttkbootstrap\src')

import tkinter as tk
from ttkbootstrap_next.widgets.button import Button
from ttkbootstrap_next.events import Event

def test_event_system_vs_direct_binding():
    """Compare event system vs direct binding for drag events."""
    print("Testing Event System vs Direct Binding for Drag Events\n")

    root = tk.Tk()
    root.title("Drag Event Test")
    root.geometry("400x300")

    # Create two buttons side by side
    frame1 = tk.Frame(root, bg='lightblue', width=200, height=300)
    frame1.pack(side='left', fill='both', expand=True)
    frame1.pack_propagate(False)

    frame2 = tk.Frame(root, bg='lightgreen', width=200, height=300)
    frame2.pack(side='right', fill='both', expand=True)
    frame2.pack_propagate(False)

    # Button 1: Using event system
    label1 = tk.Label(frame1, text="Using widget.on()", font=('Arial', 12, 'bold'), bg='lightblue')
    label1.pack(pady=10)

    btn1 = Button(parent=frame1, text="Drag Me (Event System)", variant='solid')
    btn1.attach(pady=20)

    status1 = tk.Label(frame1, text="No drag yet", bg='lightblue', wraplength=180)
    status1.pack(pady=10)

    # Button 2: Using direct binding
    label2 = tk.Label(frame2, text="Using widget.bind()", font=('Arial', 12, 'bold'), bg='lightgreen')
    label2.pack(pady=10)

    btn2 = Button(parent=frame2, text="Drag Me (Direct Bind)", variant='solid')
    btn2.attach(pady=20)

    status2 = tk.Label(frame2, text="No drag yet", bg='lightgreen', wraplength=180)
    status2.pack(pady=10)

    # Setup counters
    drag_counts = {'system': 0, 'direct': 0}

    # Method 1: Event system
    def on_system_down(event):
        drag_counts['system'] = 0
        status1.config(text=f"Mouse DOWN\nWaiting for motion...")
        print("🔵 Event System: Mouse DOWN")

    def on_system_motion(event):
        drag_counts['system'] += 1
        status1.config(text=f"DRAGGING!\nMotion events: {drag_counts['system']}")
        print(f"🔵 Event System: MOTION {drag_counts['system']}")

    def on_system_up(event):
        status1.config(text=f"Drag complete\nTotal motions: {drag_counts['system']}")
        print(f"🔵 Event System: Mouse UP (total: {drag_counts['system']})")

    btn1.on(Event.CLICK1_DOWN).listen(on_system_down)
    btn1.on(Event.DRAG1).listen(on_system_motion)
    btn1.on(Event.CLICK1_UP).listen(on_system_up)

    # Method 2: Direct binding
    def on_direct_down(event):
        drag_counts['direct'] = 0
        status2.config(text=f"Mouse DOWN\nWaiting for motion...")
        print("🟢 Direct Bind: Mouse DOWN")

    def on_direct_motion(event):
        drag_counts['direct'] += 1
        status2.config(text=f"DRAGGING!\nMotion events: {drag_counts['direct']}")
        print(f"🟢 Direct Bind: MOTION {drag_counts['direct']}")

    def on_direct_up(event):
        status2.config(text=f"Drag complete\nTotal motions: {drag_counts['direct']}")
        print(f"🟢 Direct Bind: Mouse UP (total: {drag_counts['direct']})")

    btn2.widget.bind('<ButtonPress-1>', on_direct_down, add='+')
    btn2.widget.bind('<B1-Motion>', on_direct_motion, add='+')
    btn2.widget.bind('<ButtonRelease-1>', on_direct_up, add='+')

    print("\n" + "="*50)
    print("Instructions:")
    print("1. Click and drag the LEFT button (Event System)")
    print("2. Click and drag the RIGHT button (Direct Bind)")
    print("3. Compare the motion event counts")
    print("="*50 + "\n")

    root.mainloop()

if __name__ == "__main__":
    test_event_system_vs_direct_binding()