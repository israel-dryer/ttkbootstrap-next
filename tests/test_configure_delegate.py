"""Test script for add_configure_delegate and add_configure_alias methods."""
import sys
import tkinter as tk
import os

# Fix encoding for Windows console
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

# Add src directory to path
sys.path.insert(0, r'D:\Development\ttkbootstrap\src')

from ttkbootstrap.interop.runtime.configure import ConfigureMixin


class TestWidget(ConfigureMixin):
    """Test widget to demonstrate configuration delegates."""

    def __init__(self):
        # Create a basic tkinter widget for testing
        root = tk.Tk()
        self.widget = tk.Label(root, text="Test")
        self._items = []
        self._selection = None
        super().__init__()

    def _get_items(self):
        print(f"Getting items: {self._items}")
        return self._items

    def _set_items(self, value):
        print(f"Setting items to: {value}")
        self._items = list(value)

    def _selection_accessor(self, value=None):
        if value is None:
            print(f"Getting selection: {self._selection}")
            return self._selection
        else:
            print(f"Setting selection to: {value}")
            self._selection = value


def test_basic_delegate():
    """Test basic delegate registration."""
    print("\n=== Test 1: Basic delegate registration ===")

    TestWidget.add_configure_delegate("items", "_get_items", "_set_items")

    widget = TestWidget()
    widget.configure(items=[1, 2, 3])
    result = widget.configure("items")

    assert result == [1, 2, 3], f"Expected [1, 2, 3], got {result}"
    print("✓ Basic delegate works!")


def test_delegate_with_alias():
    """Test delegate with alias."""
    print("\n=== Test 2: Delegate with alias ===")

    # Clear previous registrations
    TestWidget._configure_methods = {}
    TestWidget._configure_aliases = {}

    TestWidget.add_configure_delegate("items", "_get_items", "_set_items", aliases="data")

    widget = TestWidget()
    widget.configure(data=[4, 5, 6])
    result = widget.configure("items")

    assert result == [4, 5, 6], f"Expected [4, 5, 6], got {result}"
    print("✓ Alias works!")


def test_multiple_aliases():
    """Test multiple aliases."""
    print("\n=== Test 3: Multiple aliases ===")

    TestWidget._configure_methods = {}
    TestWidget._configure_aliases = {}

    TestWidget.add_configure_delegate("items", "_get_items", "_set_items", aliases=["data", "records"])

    widget = TestWidget()
    widget.configure(records=[7, 8, 9])
    result = widget.configure("data")

    assert result == [7, 8, 9], f"Expected [7, 8, 9], got {result}"
    print("✓ Multiple aliases work!")


def test_single_accessor():
    """Test single accessor method for both get/set."""
    print("\n=== Test 4: Single accessor method ===")

    TestWidget._configure_methods = {}
    TestWidget._configure_aliases = {}

    TestWidget.add_configure_delegate("selection", "_selection_accessor", "_selection_accessor")

    widget = TestWidget()
    widget.configure(selection="first")
    result = widget.configure("selection")

    assert result == "first", f"Expected 'first', got {result}"
    print("✓ Single accessor works!")


def test_method_chaining():
    """Test method chaining."""
    print("\n=== Test 5: Method chaining ===")

    TestWidget._configure_methods = {}
    TestWidget._configure_aliases = {}

    (TestWidget
        .add_configure_delegate("items", "_get_items", "_set_items")
        .add_configure_alias("data", "items")
        .add_configure_alias("records", "items"))

    widget = TestWidget()
    widget.configure(records=[10, 11, 12])
    result = widget.configure("data")

    assert result == [10, 11, 12], f"Expected [10, 11, 12], got {result}"
    print("✓ Method chaining works!")


def test_inheritance():
    """Test that delegates work with inheritance."""
    print("\n=== Test 6: Inheritance ===")

    # Reset base class
    TestWidget._configure_methods = {}
    TestWidget._configure_aliases = {}
    TestWidget.add_configure_delegate("items", "_get_items", "_set_items")

    class ExtendedWidget(TestWidget):
        def __init__(self):
            self._custom = None
            super().__init__()

        def _get_custom(self):
            return self._custom

        def _set_custom(self, value):
            self._custom = value

    # Add to subclass
    ExtendedWidget.add_configure_delegate("custom", "_get_custom", "_set_custom")

    widget = ExtendedWidget()
    widget.configure(items=[1, 2, 3])
    widget.configure(custom="test")

    assert widget.configure("items") == [1, 2, 3]
    assert widget.configure("custom") == "test"
    print("✓ Inheritance works!")


def test_error_handling():
    """Test error handling."""
    print("\n=== Test 7: Error handling ===")

    TestWidget._configure_methods = {}
    TestWidget._configure_aliases = {}

    try:
        TestWidget.add_configure_delegate("bad_option")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✓ Correctly raised error: {e}")


if __name__ == "__main__":
    print("Testing ConfigureMixin.add_configure_delegate() and add_configure_alias()")

    test_basic_delegate()
    test_delegate_with_alias()
    test_multiple_aliases()
    test_single_accessor()
    test_method_chaining()
    test_inheritance()
    test_error_handling()

    print("\n" + "="*50)
    print("All tests passed! ✓")
    print("="*50)
