# Backwards Compatibility

This library simulates transparency by inheriting the background color of the parent container. This means that certain
properties and methods are expected on the widget. In order to facilitate integration with existing libraries that
provide tkinter components, such as tk-table and other such libraries, a collection of `shim` mixins will be provided
that allow the widget to work with this library. Specific shims can be created for known library integrations, and a
general shim can be provided for others who which to integrate other 3rd-party library widgets.


