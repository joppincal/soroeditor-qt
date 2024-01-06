from pprint import pprint
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QPlainTextEdit, QWidget

from soroeditor import FileOperation


class ThirdPartyNoticesWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('SoroEditor - ライセンス情報')
        self.resize(600, 500)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.getThirdPartyNotices()
        self.makeLayout()

    def makeLayout(self):
        self.textedit = QPlainTextEdit(self)
        self.textedit.setReadOnly(True)
        self.textedit.setTextInteractionFlags(self.textedit.textInteractionFlags() | Qt.TextSelectableByKeyboard)
        self.listWidget = QListWidget(self)
        self.listWidget.itemSelectionChanged.connect(self.itemSelectionChanged)

        hlayout = QtWidgets.QHBoxLayout(self)
        hlayout.addWidget(self.listWidget, 20)
        hlayout.addWidget(self.textedit, 80)

        self.setThirdPartyNamesToListWidget()

    def itemSelectionChanged(self):
        self.textedit.setPlainText(ThirdPartyNotices[self.listWidget.currentItem().text()])

    def setThirdPartyNamesToListWidget(self):
        for name in ThirdPartyNotices.keys():
            QListWidgetItem(name, self.listWidget)
        self.listWidget.setCurrentRow(0)

    def getThirdPartyNotices(self):
        global ThirdPartyNotices
        ThirdPartyNotices = FileOperation.openFile('./ThirdPartyNotices.txt')
        ThirdPartyNotices = [text.lstrip('\n') for text in ThirdPartyNotices.split('\n---------------------------------------------------------\n')[0:] if text]
        ThirdPartyNotices = {text.split('\n',1)[0]:text for text in ThirdPartyNotices}
