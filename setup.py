import sys
from setuptools import setup, Extension

# Only build the winmenu extension on Windows
ext_modules = []
if sys.platform.startswith("win"):
    winmenu_ext = Extension(
        "ttkbootstrap.contrib.winmenu._native",
        sources=["src/ttkbootstrap/contrib/winmenu/_native.c"],
        libraries=["user32", "gdi32", "uxtheme"],
        optional=True,  # Don't fail if compilation fails
    )
    ext_modules.append(winmenu_ext)

setup(
    ext_modules=ext_modules,
)