from PySide6.QtWidgets import QToolBar

from .MainWindow import LineEdit, PlainTextEdit, TextEditor

__version__ = "0.4.0"

toolBars: list[QToolBar]
textEdits: list[PlainTextEdit]
lineEdits: list[LineEdit]
textEditor: TextEditor
settings: dict
projectSettings: dict
