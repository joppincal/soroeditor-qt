from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (QDialogButtonBox, QHBoxLayout, QVBoxLayout,
                               QWidget)

from soroeditor import SettingOperation


class SettingWindow(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.resize(800, 600)
        self.setWindowFlags(Qt.Dialog)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle("SoroEditor - 設定")
        self.makeLayout()

    def makeLayout(self):
        global bottomBar
        vBox = QVBoxLayout(self)
        hBox = QHBoxLayout()
        bottomBar = QDialogButtonBox()
        vBox.addLayout(hBox)
        vBox.addWidget(bottomBar)
        vBox1 = QVBoxLayout()
        vBox2 = QVBoxLayout()
        hBox.addLayout(vBox1, 1)
        hBox.addLayout(vBox2, 1)
        vBox1.addWidget(QWidget())
        vBox2.addWidget(QWidget())

        bottomBar.setStandardButtons(
            bottomBar.StandardButton.Save | bottomBar.StandardButton.Cancel
        )
        bottomBar.button(bottomBar.StandardButton.Save).setText("保存(&S)")
        bottomBar.button(bottomBar.StandardButton.Cancel).setText("キャンセル")
        bottomBar.button(bottomBar.StandardButton.Cancel)

        for button in bottomBar.buttons():
            button.clicked.connect(self.buttonClicked)

    @Slot()
    def buttonClicked(self):
        button = self.sender()
        if button == bottomBar.button(bottomBar.StandardButton.Save):
            self.saveSetting()
        if button == bottomBar.button(bottomBar.StandardButton.Cancel):
            self.close()

    def saveSetting(self):
        data = SettingOperation.DEFAULTSETTINGDATA  # 本来は、ウィンドウ内の各項目を読み取るべし
        return SettingOperation.writeSettingFile(data)
