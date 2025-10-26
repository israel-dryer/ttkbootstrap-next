"""Test script for @configure_delegate decorator."""
import sys
import tkinter as tk
import os

# Fix encoding for Windows console
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

# Add src directory to path
sys.path.insert(0, r'D:\Development\ttkbootstrap_next\src')

from ttkbootstrap_next.interop.runtime.configure import ConfigureMixin, configure_delegate


class TestWidget(ConfigureMixin):
    """Test widget using @configure_delegate decorator."""

    def __init__(self):
        # Create a basic tkinter widget for testing
        root = tk.Tk()
        self.widget = tk.Label(root, text="Test")
        self._text = "initial"
        self._items = []
        self._selection = None
        super().__init__()

    @configure_delegate("text")
    def _configure_text(self, value=None):
        """Text configuration with decorator."""
        if value is None:
            print(f"Getting text: {self._text}")
            return self._text
        else:
            print(f"Setting text to: {value}")
            self._text = value
            return self

    @configure_delegate("items", aliases="data")
    def _configure_items(self, value=None):
        """Items configuration with single alias."""
        if value is None:
            print(f"Getting items: {self._items}")
            return self._items
        else:
            print(f"Setting items to: {value}")
            self._items = list(value)
            return self

    @configure_delegate("selection", aliases=["sel", "selected"])
    def _configure_selection(self, value=None):
        """Selection configuration with multiple aliases."""
        if value is None:
            print(f"Getting selection: {self._selection}")
            return self._selection
        else:
            print(f"Setting selection to: {value}")
            self._selection = value
            return self


def test_basic_decorator():
    """Test basic decorator functionality."""
    print("\n=== Test 1: Basic decorator ===")

    widget = TestWidget()
    widget.configure(text="Hello")
    result = widget.configure("text")

    assert result == "Hello", f"Expected 'Hello', got {result}"
    print("✓ Basic decorator works!")


def test_decorator_with_alias():
    """Test decorator with single alias."""
    print("\n=== Test 2: Decorator with alias ===")

    widget = TestWidget()
    widget.configure(data=[1, 2, 3])
    result = widget.configure("items")

    assert result == [1, 2, 3], f"Expected [1, 2, 3], got {result}"

    # Test using alias to read
    result2 = widget.configure("data")
    assert result2 == [1, 2, 3], f"Expected [1, 2, 3], got {result2}"
    print("✓ Decorator with alias works!")


def test_decorator_with_multiple_aliases():
    """Test decorator with multiple aliases."""
    print("\n=== Test 3: Decorator with multiple aliases ===")

    widget = TestWidget()
    widget.configure(sel="first")
    result = widget.configure("selection")
    assert result == "first", f"Expected 'first', got {result}"

    widget.configure(selected="second")
    result = widget.configure("sel")
    assert result == "second", f"Expected 'second', got {result}"

    print("✓ Decorator with multiple aliases works!")


def test_decorator_inheritance():
    """Test that decorated methods work with inheritance."""
    print("\n=== Test 4: Decorator inheritance ===")

    class ExtendedWidget(TestWidget):
        def __init__(self):
            self._custom = None
            super().__init__()

        @configure_delegate("custom", aliases="c")
        def _configure_custom(self, value=None):
            if value is None:
                return self._custom
            self._custom = value
            return self

    widget = ExtendedWidget()

    # Parent's decorated methods should work
    widget.configure(text="Parent")
    assert widget.configure("text") == "Parent"

    # Child's decorated methods should work
    widget.configure(custom="Child")
    assert widget.configure("custom") == "Child"
    assert widget.configure("c") == "Child"  # Alias

    print("✓ Decorator inheritance works!")


def test_mixed_approaches():
    """Test mixing decorator with manual registration."""
    print("\n=== Test 5: Mixed approaches ===")

    class MixedWidget(ConfigureMixin):
        def __init__(self):
            root = tk.Tk()
            self.widget = tk.Label(root, text="Test")
            self._decorated = None
            self._manual = None
            super().__init__()

        @configure_delegate("decorated")
        def _configure_decorated(self, value=None):
            if value is None:
                return self._decorated
            self._decorated = value
            return self

        def _get_manual(self):
            return self._manual

        def _set_manual(self, value):
            self._manual = value

    # Add manual delegate after class definition
    MixedWidget.add_configure_delegate("manual", "_get_manual", "_set_manual", aliases="m")

    widget = MixedWidget()

    # Decorated should work
    widget.configure(decorated="dec")
    assert widget.configure("decorated") == "dec"

    # Manual should work
    widget.configure(manual="man")
    assert widget.configure("manual") == "man"
    assert widget.configure("m") == "man"

    print("✓ Mixed approaches work!")


def test_check_registered_methods():
    """Verify that decorated methods are properly registered."""
    print("\n=== Test 6: Verify registration ===")

    widget = TestWidget()

    # Check that _configure_methods was populated
    assert "text" in widget._configure_methods
    assert "items" in widget._configure_methods
    assert "selection" in widget._configure_methods

    # Check that aliases were registered
    assert "data" in widget._configure_aliases
    assert "sel" in widget._configure_aliases
    assert "selected" in widget._configure_aliases

    # Verify mappings
    assert widget._configure_aliases["data"] == "items"
    assert widget._configure_aliases["sel"] == "selection"
    assert widget._configure_aliases["selected"] == "selection"

    print("✓ Methods and aliases properly registered!")


if __name__ == "__main__":
    print("Testing @configure_delegate decorator")

    test_basic_decorator()
    test_decorator_with_alias()
    test_decorator_with_multiple_aliases()
    test_decorator_inheritance()
    test_mixed_approaches()
    test_check_registered_methods()

    print("\n" + "="*50)
    print("All decorator tests passed! ✓")
    print("="*50)