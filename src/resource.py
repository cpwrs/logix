"""
resource.py
Carson Powers

Handles reassigning the path of a resource
b/c PyInstaller stores temp files in _MEIPASS
"""


import sys
import os


def path(relative_path):
    try:
        base = sys._MEIPASS
    except Exception:
        base = os.path.abspath(".")

    return os.path.join(base, relative_path)
