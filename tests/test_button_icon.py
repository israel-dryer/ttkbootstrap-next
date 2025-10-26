"""Test Button icon configuration with decorator."""
import sys
import os

# Fix encoding for Windows console
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

# Add src directory to path
sys.path.insert(0, r'D:\Development\ttkbootstrap\src')

import tkinter as tk
from ttkbootstrap_next.widgets.button import Button
from ttkbootstrap_next.core.mixins.icon import IconMixin

def test_button_icon():
    """Test that button icon configuration works."""
    print("Testing Button icon configuration...")

    root = tk.Tk()
    root.withdraw()  # Don't show window

    try:
        # Create button
        button = Button(parent=root, text="Test")
        print(f"✓ Button created")

        # Debug: Check what's registered
        print(f"\nDebug - Button MRO: {[c.__name__ for c in Button.__mro__]}")
        print(f"Debug - Button._configure_methods: {Button._configure_methods}")
        print(f"Debug - Button._configure_aliases: {Button._configure_aliases}")

        # Try to configure icon
        print("Attempting to configure icon...")
        button.configure(icon="house-fill")
        print(f"✓ Icon configured successfully")

        # Try to read icon
        icon = button.configure("icon")
        print(f"✓ Icon value: {icon}")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        root.destroy()

if __name__ == "__main__":
    test_button_icon()
