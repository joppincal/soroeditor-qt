from logging import Logger

from PySide6.QtWidgets import QToolBar

from soroeditor_qt.MainWindow import LineEdit, PlainTextEdit, TextEditor

__version__ = "0.4.0"

logger: Logger
toolBars: list[QToolBar]
textEdits: list[PlainTextEdit]
lineEdits: list[LineEdit]
textEditor: TextEditor
settings: dict
projectSettings: dict
