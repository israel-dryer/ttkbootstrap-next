"""Test to debug why drag widget bindings don't work in list context."""
import sys
import os

# Fix encoding for Windows console
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

# Add src directory to path
sys.path.insert(0, r'D:\Development\ttkbootstrap\src')

import tkinter as tk
from ttkbootstrap.widgets.button import Button
from ttkbootstrap.events import Event

def test_drag_widget_created_immediately():
    """Test event binding when widget is created immediately."""
    print("=== Test 1: Widget Created Immediately ===\n")

    root = tk.Tk()
    root.title("Immediate Creation Test")
    root.geometry("400x200")

    frame = tk.Frame(root, bg='lightblue')
    frame.pack(fill='both', expand=True)

    status = tk.Label(frame, text="No drag yet", bg='lightblue')
    status.pack(pady=10)

    # Create widget immediately (don't attach yet)
    btn = Button(parent=frame, text="Drag Me", variant='solid')
    btn.widget.pack(pady=20)

    drag_counts = {'count': 0}

    def on_down(event):
        drag_counts['count'] = 0
        status.config(text="Mouse DOWN")
        print("✓ DOWN event fired")

    def on_motion(event):
        drag_counts['count'] += 1
        status.config(text=f"DRAGGING: {drag_counts['count']}")
        if drag_counts['count'] <= 3:
            print(f"✓ MOTION event {drag_counts['count']}")

    def on_up(event):
        status.config(text=f"Done: {drag_counts['count']} motions")
        print(f"✓ UP event fired (total: {drag_counts['count']})")

    # Bind using event system
    btn.on(Event.CLICK1_DOWN).listen(on_down)
    btn.on(Event.DRAG1).listen(on_motion)
    btn.on(Event.CLICK1_UP).listen(on_up)

    print("Bindings added. Try dragging the button.")
    root.mainloop()

def test_drag_widget_created_via_after_idle():
    """Test event binding when widget is created via after_idle."""
    print("\n=== Test 2: Widget Created via after_idle ===\n")

    root = tk.Tk()
    root.title("Lazy Creation Test")
    root.geometry("400x200")

    frame = tk.Frame(root, bg='lightgreen')
    frame.pack(fill='both', expand=True)

    status = tk.Label(frame, text="Widget not created yet...", bg='lightgreen')
    status.pack(pady=10)

    drag_counts = {'count': 0}
    btn_holder = {'btn': None}

    def create_and_bind_widget():
        """Create widget and add bindings in idle callback."""
        print("Creating widget in after_idle...")

        btn = Button(parent=frame, text="Drag Me (Lazy)", variant='solid')
        btn.attach(pady=20)
        btn_holder['btn'] = btn

        def on_down(event):
            drag_counts['count'] = 0
            status.config(text="Mouse DOWN")
            print("✓ DOWN event fired (lazy)")

        def on_motion(event):
            drag_counts['count'] += 1
            status.config(text=f"DRAGGING: {drag_counts['count']}")
            if drag_counts['count'] <= 3:
                print(f"✓ MOTION event {drag_counts['count']} (lazy)")

        def on_up(event):
            status.config(text=f"Done: {drag_counts['count']} motions")
            print(f"✓ UP event fired (total: {drag_counts['count']}) (lazy)")

        # Bind using event system AFTER creation
        print("Adding bindings...")
        btn.on(Event.CLICK1_DOWN).listen(on_down)
        btn.on(Event.DRAG1).listen(on_motion)
        btn.on(Event.CLICK1_UP).listen(on_up)
        print("Bindings added. Try dragging the button.")

        status.config(text="Widget created! Try dragging...")

    # Schedule widget creation
    root.after_idle(create_and_bind_widget)

    root.mainloop()

if __name__ == "__main__":
    # Run test 1 first
    test_drag_widget_created_immediately()

    # Then run test 2
    # test_drag_widget_created_via_after_idle()
