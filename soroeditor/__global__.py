from logging import Logger
from PySide6.QtWidgets import QToolBar
from soroeditor.MainWindow import TextEditor, PlainTextEdit, LineEdit

logger: Logger
toolBars: list[QToolBar]
textEdits: list[PlainTextEdit]
lineEdits: list[LineEdit]
textEditor: TextEditor
