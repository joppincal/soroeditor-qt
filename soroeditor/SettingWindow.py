from typing import Optional
from PySide6 import QtWidgets
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget

from soroeditor.Icon import Icon

class SettingWindow(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.resize(800, 600)
        self.setWindowFlags(Qt.Dialog)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle('SoroEditor - 設定')
