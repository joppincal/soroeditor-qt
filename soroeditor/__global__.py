from logging import Logger
from PySide6.QtWidgets import QToolBar
from soroeditor.MainWindow import TextEditor, PlainTextEdit, LineEdit

__version__ = "0.1.0"

logger: Logger
toolBars: list[QToolBar]
textEdits: list[PlainTextEdit]
lineEdits: list[LineEdit]
textEditor: TextEditor
settings: dict
projectSettings: dict
