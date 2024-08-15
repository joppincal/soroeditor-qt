from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QWidget,
)

from . import FileOperation


class ThirdPartyNoticesWindow(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setWindowTitle("SoroEditor - ライセンス情報")
        self.resize(700, 500)
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.getThirdPartyNotices()
        self.makeLayout()

    def makeLayout(self):
        self.textedit = QPlainTextEdit(self)
        self.textedit.setReadOnly(True)
        self.textedit.setTextInteractionFlags(
            self.textedit.textInteractionFlags() | Qt.TextSelectableByKeyboard
        )

        fontCandidates = [
            "Consolas",
            "SF Mono",
            "DejaVu Sans Mono",
            "Courier New",
            "Courier",
        ]
        selectedFont = None

        for family in QFontDatabase.families():
            if family in fontCandidates:
                selectedFont = family
                break

        if not selectedFont:
            selectedFont = QFontDatabase.systemFont(QFontDatabase.FixedFont)

        font = QFont(selectedFont)
        self.textedit.setFont(font)

        self.listWidget = QListWidget(self)
        self.listWidget.itemSelectionChanged.connect(self.itemSelectionChanged)

        hlayout = QtWidgets.QHBoxLayout(self)
        hlayout.addWidget(self.listWidget, 20)
        hlayout.addWidget(self.textedit, 80)

        self.setThirdPartyNamesToListWidget()

    def itemSelectionChanged(self):
        self.textedit.setPlainText(
            ThirdPartyNotices[self.listWidget.currentItem().text()]
        )

    def setThirdPartyNamesToListWidget(self):
        for name in ThirdPartyNotices.keys():
            QListWidgetItem(name, self.listWidget)
        self.listWidget.setCurrentRow(0)

    def getThirdPartyNotices(self):
        global ThirdPartyNotices
        ThirdPartyNotices = FileOperation.openFile("./ThirdPartyNotices.txt")
        ThirdPartyNotices = [
            text.lstrip("\n").rstrip("\n")
            for text in ThirdPartyNotices.split(
                "\n---------------------------------------------------------\n"
            )[0:]
            if text
        ]
        ThirdPartyNotices = {
            text.split("\n", 1)[0]: text for text in ThirdPartyNotices
        }

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Escape, Qt.Key_Return):
            self.close()
        return super().keyPressEvent(event)
