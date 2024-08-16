from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QWidget

from . import __global__, __version__
from .Icon import Icon


class AboutWindow(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowType.Dialog)
        self.setWindowTitle("SoroEditorについて")
        self.setFixedSize(300, 500)
        self.makeLayout()

    def makeLayout(self):
        icon = QLabel("SoroEditorアイコン")
        icon.setPixmap(Icon().Icon.scaled(256, 256))
        QFont
        self.font()
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label.setFont(QFont(label.font().family(), 11))
        label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        label.setOpenExternalLinks(True)
        label.setText(
            f"<p>SoroEditor そろエディタ</p>"
            f"<p>Author: Joppincal</p><p>Version: {__version__.__version__}</p>"
            f'<a href="https://github.com/joppincal/soroeditor-qt">Github</a>'
        )

        vlayout = QtWidgets.QVBoxLayout(self)
        vlayout.addWidget(icon, 2, Qt.AlignmentFlag.AlignHCenter)
        vlayout.addWidget(label, 1, Qt.AlignmentFlag.AlignHCenter)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Escape, Qt.Key_Return):
            self.close()
        return super().keyPressEvent(event)
