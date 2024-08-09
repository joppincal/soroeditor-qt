import copy

from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
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

from soroeditor_qt import SettingOperation
from soroeditor_qt import __global__ as _g


class SettingWindow(QWidget):
    def __init__(self, parent: QWidget, mode: str = "Default") -> None:
        super().__init__(parent)
        if mode not in ("Default", "Project"):
            mode = "Default"

        self.mode = mode
        self.dataByMode: dict = {}
        if mode == "Default":
            self.dataByMode["Settings"] = _g.settings
            self.dataByMode["WindowTitle"] = "デフォルト設定"
            self.dataByMode["SaveSuccessMessage"] = (
                "SoroEditor - Infomation",
                "設定を保存しました",
            )
            self.dataByMode["SaveFailedMessage"] = (
                "SoroEditor - Error",
                "設定の保存に失敗しました",
            )
        elif mode == "Project":
            self.dataByMode["Settings"] = _g.projectSettings
            self.dataByMode["WindowTitle"] = "プロジェクト設定"
            self.dataByMode["SaveSuccessMessage"] = (
                "SoroEditor - Infomation",
                "プロジェクト設定はプロジェクトファイルの保存時に保存されます",
            )
            self.dataByMode["SaveFailedMessage"] = (
                "SoroEditor - Error",
                "設定の保存に失敗しました",
            )
        self.resize(600, 500)
        self.setFont(QFont(self.font().family(), 10))
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle("SoroEditor - " + self.dataByMode["WindowTitle"])
        self.makeLayout()
        self.setSettings(self.dataByMode["Settings"])

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
        fontComboBox.setEditable(True)
        fontComboBox.setMaxCount(fontComboBox.count())
        # スタイル
        fontStyleComboBox = QComboBox()
        fontStyleComboBox.setEditable(True)
        # フォントサイズ
        fontSizeComboBox = QComboBox()
        fontSizeComboBox.addItems(
            [str(i) for i in list(range(1, 101)).__reversed__()]
        )
        fontSizeComboBox.setEditable(True)
        if self.style().name() == "windows11":
            for lineEdit in {
                comboBox.findChild(QLineEdit)
                for comboBox in {
                    fontComboBox,
                    fontStyleComboBox,
                    fontSizeComboBox,
                }
            }:
                lineEdit.setTextMargins(-9, 0, 0, 0)
        # ウィンドウサイズ
        screens = QGuiApplication.screens()
        sizeCandidate = []
        for screen in screens:
            ratio = screen.devicePixelRatio()
            size = [
                length * ratio
                for length in [screen.size().width(), screen.size().height()]
            ]
            sizeCandidate.extend(
                [
                    f"{int(size[0] * li[0])}*{int(size[1] * li[1])}"
                    for li in [[0.8, 0.8], [0.8, 0.6], [0.6, 0.6], [0.5, 0.5]]
                ]
            )
        windowSizeComboBox = QComboBox()
        windowSizeComboBox.addItems(sizeCandidate + ["Maximize", "FullScreen"])
        # リサイズ可能チェックボックス
        resizeableCheckbox = QCheckBox("手動でのリサイズを許可")
        # vBox1へウィジェットを追加
        self.widgetsForVBox1 = [
            QLabel("フォントファミリ"),
            fontComboBox,
            QLabel("フォントスタイル"),
            fontStyleComboBox,
            QLabel("フォントサイズ"),
            fontSizeComboBox,
            QLabel("ウィンドウサイズ"),
            windowSizeComboBox,
            resizeableCheckbox,
        ]
        self.addWidgetsFor(vBox1, self.widgetsForVBox1)
        vBox1.addStretch(1)

        # スロットを紐付け
        fontComboBox.currentIndexChanged.connect(self.setFontStyleNames)
        fontComboBox.currentIndexChanged.connect(self.setComboBoxFont)
        fontStyleComboBox.currentIndexChanged.connect(self.setComboBoxFont)

        # vBox2: 右側
        # ツールバー・ステータスバー
        buttonForToolBarSetting = QPushButton()
        buttonForToolBarSetting.setObjectName("buttonForToolBarSetting")
        buttonForToolBarSetting.setText("ツールバー設定")
        buttonForToolBarSetting.clicked.connect(self.buttonClicked)

        self.widgetsForVBox2 = [buttonForToolBarSetting]
        vBox2.addWidget(buttonForToolBarSetting)
        vBox2.addStretch(1)
        # vBox2.addStretch(1)

        # ボトムバー
        bottomBarBox = QHBoxLayout()
        self.dialogButtonBox = QDialogButtonBox()
        self.dialogButtonBox.setStandardButtons(
            self.dialogButtonBox.StandardButton.Save
            | self.dialogButtonBox.StandardButton.Cancel
        )
        self.dialogButtonBox.button(
            self.dialogButtonBox.StandardButton.Save
        ).setText("保存(&S)")
        self.dialogButtonBox.button(
            self.dialogButtonBox.StandardButton.Cancel
        ).setText("終了(&C)")
        for button in self.dialogButtonBox.buttons():
            button.clicked.connect(self.buttonClicked)
        # 設定適用範囲設定チェックボックス
        self.settingCoverageCheckbox = QCheckBox()
        if self.mode == "Default":
            checkBoxText = "現在"
            self.settingCoverageCheckbox.setChecked(True)
        elif self.mode == "Project":
            checkBoxText = "次回以降"
        self.settingCoverageCheckbox.setText(
            "変更内容を" + checkBoxText + "のプロジェクトにも反映する"
        )
        # bottomBarBoxにウィジェットを追加
        bottomBarBox.addStretch(1)
        bottomBarBox.addWidget(self.settingCoverageCheckbox)
        bottomBarBox.addWidget(self.dialogButtonBox)

        vBox.addLayout(bottomBarBox)

        self.setFixedSize(self.size())

    @QtCore.Slot()
    def buttonClicked(self):
        button = self.sender()
        if button == self.dialogButtonBox.button(
            self.dialogButtonBox.StandardButton.Save
        ):
            if self.saveSetting():
                QMessageBox.information(
                    self, *self.dataByMode["SaveSuccessMessage"]
                )
                self.close()
            else:
                QMessageBox.warning(
                    self, *self.dataByMode["SaveFailedMessage"]
                )
        if button == self.dialogButtonBox.button(
            self.dialogButtonBox.StandardButton.Cancel
        ):
            self.close()
        if button.objectName() == "buttonForToolBarSetting":
            ToolBarSettingWindow(self)

    @QtCore.Slot()
    def setFontStyleNames(self):
        family = self.widgetsForVBox1[1].currentText()
        font = QFont(family)
        fontStyleNames = QFontDatabase.styles(family)
        comboBox = self.widgetsForVBox1[3]

        comboBox.clear()
        comboBox.setMaxCount(len(fontStyleNames))
        comboBox.addItems(fontStyleNames)

        for i, styleName in enumerate(fontStyleNames):
            font.setStyleName(styleName)
            comboBox.setItemData(i, font, Qt.FontRole)

    @QtCore.Slot()
    def setComboBoxFont(self):
        family = self.widgetsForVBox1[1].currentText()
        styleName = self.widgetsForVBox1[3].currentText()

        font = QFont(family)
        styledFont = QFont(font)
        styledFont.setStyleName(styleName)

        self.widgetsForVBox1[1].setFont(font)
        self.widgetsForVBox1[3].setFont(styledFont)

    def saveSetting(self) -> bool:
        self.dataByMode["Settings"]["Font"] = self.widgetsForVBox1[
            1
        ].currentText()
        self.dataByMode["Settings"]["FontStyle"] = self.widgetsForVBox1[
            3
        ].currentText()
        fontSize = self.widgetsForVBox1[5].currentText()
        try:
            fontSize = int(fontSize)
        except ValueError:
            fontSize = None
        self.dataByMode["Settings"]["FontSize"] = fontSize

        size = self.widgetsForVBox1[7].currentText()
        if "*" in size:
            size = size.split("*")
            try:
                size = [int(num) for num in size]
            except ValueError:
                size = None
        if type(size) is not list and size not in ("Maximize", "FullScreen"):
            size = None
        self.dataByMode["Settings"]["Size"] = size

        resizable = self.widgetsForVBox1[8].isChecked()
        self.dataByMode["Settings"]["Resizable"] = resizable

        self.dataByMode["Settings"] = SettingOperation.settingVerification(
            self.dataByMode["Settings"]
        )

        if self.mode == "Default":
            if self.settingCoverageCheckbox.isChecked():
                _g.projectSettings = copy.deepcopy(self.dataByMode["Settings"])
            ret = SettingOperation.writeSettingFile(
                self.dataByMode["Settings"]
            )
        elif self.mode == "Project":
            if self.settingCoverageCheckbox.isChecked():
                _g.settings = copy.deepcopy(self.dataByMode["Settings"])
                ret = SettingOperation.writeSettingFile(
                    self.dataByMode["Settings"]
                )
            else:
                ret = True
        else:
            ret = False

        self.parent().reflectionSettings("All")  # type: ignore

        return ret

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

        fontStyle = settings.get("FontStyle", default["FontStyle"])
        if fontStyle not in QFontDatabase.styles(font):
            fontStyle = QFontDatabase.styles(font)[0]
        self.widgetsForVBox1[3].setCurrentIndex(
            QFontDatabase.styles(font).index(fontStyle)
        )

        fontSize = settings.get("FontSize", default["FontSize"])
        if type(fontSize) is not int:
            fontSize = default["FontSize"]
        self.widgetsForVBox1[5].setCurrentIndex(
            self.widgetsForVBox1[5].count() - fontSize
        )

        windowSize = settings.get("Size", default["Size"])
        if type(windowSize) is list:
            windowSize = "*".join([str(i) for i in windowSize])
        elif windowSize in ("Maximize", "FullScreen"):
            pass
        else:
            windowSize = default["Size"]
        for _ in range(2):
            self.widgetsForVBox1[7].insertSeparator(0)
        self.widgetsForVBox1[7].insertItem(0, windowSize)
        self.widgetsForVBox1[7].setCurrentIndex(0)

        resizable = settings.get("Resizable", default["Resizable"])
        if isinstance(resizable, bool):
            pass
        else:
            resizable = default["Resizable"]
        self.widgetsForVBox1[8].setChecked(resizable)


class ToolBarSettingWindow(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent, Qt.WindowType.Dialog)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.resize(1000, 500)
        self.setWindowTitle(self.parent().windowTitle() + "/ツールバー")  # type: ignore # noqa: E501
        self.mode = self.parent().mode  # type: ignore
        self.dataByMode = self.parent().dataByMode  # type: ignore

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

        self.setSettings(self.dataByMode["Settings"]["ToolBar"])

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
                    self, *self.dataByMode["SaveSuccessMessage"]
                )
                self.close()
            else:
                QMessageBox.warning(
                    self, *self.dataByMode["SaveFailedMessage"]
                )
        if button == self.bottomBar.button(
            self.bottomBar.StandardButton.Cancel
        ):
            self.close()

    def saveToolBarSetting(self):
        data = {}
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
            contents = []
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

        self.dataByMode["Settings"]["ToolBar"] = data

        self.parent().parent().reflectionSettings("All")  # type: ignore

        if self.mode == "Default":
            if self.parent().settingCoverageCheckbox.isChecked():
                _g.projectSettings = copy.deepcopy(self.dataByMode["Settings"])
            return SettingOperation.writeSettingFile(
                self.dataByMode["Settings"]
            )
        elif self.mode == "Project":
            if self.parent().settingCoverageCheckbox.isChecked():
                _g.settings = copy.deepcopy(self.dataByMode["Settings"])
                return SettingOperation.writeSettingFile(
                    self.dataByMode["Settings"]
                )
            else:
                return True
        else:
            return False

    def setSettings(self, settings: dict):
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
                        comboBox.setCurrentText(contentName)  # type: ignore
                        break
