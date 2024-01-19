from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialogButtonBox,
    QFontComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from soroeditor import SettingOperation


class SettingWindow(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.settings = self.parent().settings  # type: ignore
        self.resize(600, 500)
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle("SoroEditor - 設定")
        self.makeLayout()
        self.setSettings(self.settings)

    def makeLayout(self):
        # 全体の形
        vBox = QVBoxLayout(self)
        hBox = QHBoxLayout()
        vBox.addLayout(hBox)
        vBox1 = QVBoxLayout()
        vBox2 = QVBoxLayout()
        hBox.addLayout(vBox1, 1)
        hBox.addLayout(vBox2, 1)

        # vBox1: 左側
        # フォント
        # ファミリ
        fontComboBox = QFontComboBox()
        fontComboBox.setEditable(False)
        # フォントサイズ
        fontSizeComboBox = QComboBox()
        fontSizeComboBox.addItems(
            [str(i) for i in list(range(1, 101)).__reversed__()]
        )
        fontSizeComboBox.setEditable(True)
        # ウィンドウサイズ
        windowSizeComboBox = QComboBox()
        windowSizeComboBox.addItems(
            ["800*600", "1200*600", "1200*800", "FullScreen"]
        )
        # vBox1へウィジェットを追加
        self.widgetsForVBox1 = [
            QLabel("フォントファミリ"),
            fontComboBox,
            QLabel("フォントサイズ"),
            fontSizeComboBox,
            QLabel("ウィンドウサイズ"),
            windowSizeComboBox,
        ]
        self.addWidgetsFor(vBox1, self.widgetsForVBox1)
        vBox1.addStretch(1)

        # vBox2: 右側
        # ツールバー・ステータスバー
        buttonForToolBarSetting = QPushButton()
        buttonForToolBarSetting.setObjectName("buttonForToolBarSetting")
        buttonForToolBarSetting.setText("ツールバー設定")
        buttonForToolBarSetting.clicked.connect(self.buttonClicked)

        self.widgetsForVBox2 = [buttonForToolBarSetting]
        self.addWidgetsFor(vBox2, self.widgetsForVBox2)
        vBox2.addStretch(1)

        # ボトムバー
        self.bottomBar = QDialogButtonBox()
        self.bottomBar.setStandardButtons(
            self.bottomBar.StandardButton.Save
            | self.bottomBar.StandardButton.Cancel
        )
        self.bottomBar.button(self.bottomBar.StandardButton.Save).setText(
            "保存(&S)"
        )
        self.bottomBar.button(self.bottomBar.StandardButton.Cancel).setText(
            "終了(&C)"
        )
        for button in self.bottomBar.buttons():
            button.clicked.connect(self.buttonClicked)
        vBox.addWidget(self.bottomBar, alignment=Qt.AlignmentFlag.AlignBottom)

    @QtCore.Slot()
    def buttonClicked(self):
        button = self.sender()
        if button == self.bottomBar.button(self.bottomBar.StandardButton.Save):
            if self.saveSetting():
                QMessageBox.information(
                    self, "SoroEditor - Infomation", "設定を保存しました"
                )
                self.close()
            else:
                QMessageBox.warning(self, "SoroEditor - Error", "設定の保存に失敗しました")
        if button == self.bottomBar.button(
            self.bottomBar.StandardButton.Cancel
        ):
            self.close()
        if button.objectName() == "buttonForToolBarSetting":
            ToolBarSettingWindow(self, Qt.WindowType.Dialog)

    def saveSetting(self):
        default = SettingOperation.defaultSettingData()
        data = SettingOperation.defaultSettingData()
        data["Font"] = self.widgetsForVBox1[1].currentText()

        fontSize = self.widgetsForVBox1[3].currentText()
        try:
            fontSize = int(fontSize)
        except ValueError:
            fontSize = default["FontSize"]
        data["FontSize"] = fontSize

        size = self.widgetsForVBox1[5].currentText()
        if "*" in size:
            size = size.split("*")
            try:
                size = [int(num) for num in size]
            except ValueError:
                size = None
        if type(size) is not list and size != "FullScreen":
            size = default["Size"]
        data["Size"] = size

        data["ToolBar"] = self.settings["ToolBar"]
        data["FileHistory"] = self.settings["FileHistory"]

        self.settings = data
        self.parent().settings = self.settings
        self.parent().reflectionSettings("All")

        return SettingOperation.writeSettingFile(data)

    def addWidgetsFor(
        self, layout: QHBoxLayout | QVBoxLayout, widgets: list[QWidget]
    ):
        for widget in widgets:
            layout.addWidget(widget)

    def setSettings(self, settings: dict):
        default = SettingOperation.defaultSettingData()

        font = settings.get("Font", default["Font"])
        if font not in QFontDatabase.families(QFontDatabase.WritingSystem.Any):
            font = QFont().defaultFamily()
        self.widgetsForVBox1[1].setCurrentFont(font)

        fontSize = settings.get("FontSize", default["FontSize"])
        if type(fontSize) is not int:
            fontSize = default["FontSize"]
        self.widgetsForVBox1[3].setCurrentText(str(fontSize))
        self.widgetsForVBox1[3].setCurrentIndex(100 - fontSize)

        windowSize = settings.get("Size", default["Size"])
        if type(windowSize) is list:
            windowSize = "*".join([str(i) for i in windowSize])
        elif windowSize == "FullScreen":
            pass
        else:
            windowSize = default["Size"]
        self.widgetsForVBox1[5].setCurrentText(windowSize)


class ToolBarSettingWindow(QWidget):
    def __init__(self, parent: QWidget, f: Qt.WindowType) -> None:
        super().__init__(parent, f)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.resize(1000, 500)
        vBox = QVBoxLayout(self)
        vBoxContainContents = QVBoxLayout()
        vBox.addLayout(vBoxContainContents)
        hBoxesContainTitle = [QHBoxLayout() for _ in range(6)]
        hBoxesContainComboBoxes = [QHBoxLayout() for _ in range(6)]
        self.comboBoxesList: list[list[QWidget]] = []
        self.lineEdits: list[QLineEdit] = []
        self.checkBoxes: list[QCheckBox] = []
        self.comboBoxesContainArea: list[QComboBox] = []
        self.contentPairs = [
            ["", ""],
            ["ボタン - 新規作成", "NewFile"],
            ["ボタン - ファイルを開く", "OpenFile"],
            ["ボタン - 保存", "SaveFile"],
            ["ボタン - 名前をつけて保存", "SaveFileAs"],
            ["ボタン - インポート", "Import"],
            ["ボタン - エクスポート", "Export"],
            ["ボタン - ファイル履歴", "FileHistory"],
            ["ボタン - 終了", "Exit"],
            ["ボタン - カット", "Cut"],
            ["ボタン - コピー", "Copy"],
            ["ボタン - ペースト", "Paste"],
            ["ボタン - 取り消し", "Undo"],
            ["ボタン - 取り消しを戻す", "Redo"],
            ["ボタン - ブックマーク", "Bookmark"],
            ["ボタン - テンプレート", "Template"],
            ["ボタン - プロジェクト設定", "ProjectSetting"],
            ["ボタン - 設定", "Setting"],
            ["現在位置", "CurrentPlace"],
            ["ホットキー1", "HotKeys1"],
            ["ホットキー2", "HotKeys2"],
            ["ホットキー3", "HotKeys3"],
            ["顔文字", "Kaomoji"],
            ["時計", "Clock"],
            ["カウントダウン", "CountDown"],
            ["ストップウォッチ", "StopWatch"],
            ["ステータスバー初期メッセージ", "StatusBarMessage"],
        ]

        for i, hBoxContainComboBox, hBoxContainTitle in zip(
            range(1, 7), hBoxesContainComboBoxes, hBoxesContainTitle
        ):
            lineEdit = QLineEdit()
            lineEdit.setText(f"ツールバー{i}")
            self.lineEdits.append(lineEdit)

            checkBox = QCheckBox()
            checkBox.setText("表示切り替え")
            self.checkBoxes.append(checkBox)

            comboBoxContainArea = QComboBox()
            comboBoxContainArea.addItems(["Top", "Bottom", "Left", "Right"])
            self.comboBoxesContainArea.append(comboBoxContainArea)

            self.addWidgetsFor(
                hBoxContainTitle, [lineEdit, comboBoxContainArea, checkBox]
            )

            comboBoxes: list[QWidget] = [QComboBox() for _ in range(6)]
            for comboBox in comboBoxes:
                comboBox.addItems(  # type: ignore
                    [part[0] for part in self.contentPairs]
                )
            self.comboBoxesList.append(comboBoxes)
            self.addWidgetsFor(hBoxContainComboBox, comboBoxes)

            vBoxContainContents.addLayout(hBoxContainTitle)
            vBoxContainContents.addStretch(1)
            vBoxContainContents.addLayout(hBoxContainComboBox)
            vBoxContainContents.addStretch(4)

        # ボトムバー
        self.bottomBar = QDialogButtonBox()
        self.bottomBar.setStandardButtons(
            self.bottomBar.StandardButton.Save
            | self.bottomBar.StandardButton.Cancel
        )
        self.bottomBar.button(self.bottomBar.StandardButton.Save).setText(
            "保存(&S)"
        )
        self.bottomBar.button(self.bottomBar.StandardButton.Cancel).setText(
            "終了(&C)"
        )
        for button in self.bottomBar.buttons():
            button.clicked.connect(self.buttonClicked)
        vBox.addWidget(self.bottomBar, alignment=Qt.AlignmentFlag.AlignBottom)

        self.setSettings()

        self.show()

    def addWidgetsFor(
        self, layout: QHBoxLayout | QVBoxLayout, widgets: list[QWidget]
    ):
        for widget in widgets:
            layout.addWidget(widget)

    @QtCore.Slot()
    def buttonClicked(self):
        button = self.sender()
        if button == self.bottomBar.button(self.bottomBar.StandardButton.Save):
            if self.saveToolBarSetting():
                QMessageBox.information(
                    self, "SoroEditor - Infomation", "設定を保存しました"
                )
                self.close()
            else:
                QMessageBox.warning(self, "SoroEditor - Error", "設定の保存に失敗しました")
        if button == self.bottomBar.button(
            self.bottomBar.StandardButton.Cancel
        ):
            self.close()

    def saveToolBarSetting(self) -> bool:
        data: dict[int, dict] = {}
        checks = [checkBox.isChecked() for checkBox in self.checkBoxes]
        areas = [
            comboBox.currentText() for comboBox in self.comboBoxesContainArea
        ]
        titles = [lineEdit.text() for lineEdit in self.lineEdits]
        contentsList = [
            [comboBox.currentText() for comboBox in comboBoxes]  # type: ignore
            for comboBoxes in self.comboBoxesList
        ]
        contentsList = []
        for comboBoxes in self.comboBoxesList:
            contents: list[str] = []
            for comboBox in comboBoxes:
                text = comboBox.currentText()  # type: ignore
                for contentName, contentValue in self.contentPairs:
                    if text and text == contentName:
                        contents.append(contentValue)
                        break
            if contents:
                contentsList.append(contents)

        for i, check, area, title, contents in zip(
            range(1, 7), checks, areas, titles, contentsList
        ):
            data[i] = {
                "Enable": check,
                "Area": area,
                "Title": title,
                "Contents": contents,
            }

        self.parent().settings["ToolBar"] = data  # type: ignore
        self.parent().parent().settings["ToolBar"] = data  # type: ignore

        self.parent().parent().reflectionSettings("All")  # type: ignore

        return SettingOperation.writeSettingFile(
            self.parent().settings  # type: ignore
        )

    def setSettings(self):
        settings = SettingOperation.openSettingFile()["ToolBar"]
        for (
            checkBox,
            comboBoxContainArea,
            lineEdit,
            comboBoxes,
            setting,
        ) in zip(
            self.checkBoxes,
            self.comboBoxesContainArea,
            self.lineEdits,
            self.comboBoxesList,
            settings.values(),
        ):
            check = setting.get("Enable", False)
            if type(check) is not bool:
                check = False
            area = setting.get("Area", "Top")
            if area not in ("Top", "Bottom", "Left", "Right"):
                area = "Top"
            title = str(setting.get("Title", ""))
            contents = setting.get("Contents", [])
            if type(contents) is not list:
                contents = []

            checkBox.setChecked(check)
            comboBoxContainArea.setCurrentText(area)
            lineEdit.setText(title)
            for comboBox, content in zip(comboBoxes, contents):
                for contentName, contentValue in self.contentPairs:
                    if content == contentValue:
                        comboBox.setCurrentText(contentName)
                        break
