import copy
import os
import sys

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QFocusEvent,
    QKeySequence,
    QPixmap,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QScrollBar,
    QSplashScreen,
    QWidget,
)

from soroeditor import DataOperation, SettingOperation
from soroeditor import __global__ as _g
from soroeditor.AboutWindow import AboutWindow
from soroeditor.Icon import Icon
from soroeditor.SettingWindow import SettingWindow
from soroeditor.ThirdPartyNoticesWindow import ThirdPartyNoticesWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        pixmap = QPixmap("soroeditor/src/splash.png")
        splash = QSplashScreen(pixmap)
        splash.setWindowFlags(Qt.SplashScreen | Qt.WindowStaysOnTopHint)
        splash.show()

        self.settings = self.openSettingFile()
        self.resize(*self.settings["Size"])
        self.setWindowTitle("SoroEditor")
        self.setWindowIcon(Icon().Icon)

        self.makeLayout()

        self.currentFilePath = ""
        self.latestData = {i: {"text": "", "title": ""} for i in range(3)}

        if len(sys.argv) >= 2:
            if os.path.isfile(sys.argv[1]):
                sys.argv[1] = os.path.abspath(sys.argv[1]).replace("\\", "/")
                data = DataOperation.openProjectFile(sys.argv[1])
                if type(data) is dict:
                    DataOperation.setTextInTextBoxes(data)
                    self.currentFilePath = sys.argv[1]
                    self.latestData = data

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.loop)
        self.timer.start()

        self.show()
        splash.hide()

    def makeLayout(self):
        self.makeQActions()
        self.makeTextEditor()
        self.makeToolBar()
        self.makeMenu()
        self.setCentralWidget(_g.textEditor)

    def makeMenu(self):
        menuBar = self.menuBar()
        global menu
        menu = {
            "fileMenu": menuBar.addMenu("ファイル(&F)"),
            "editMenu": menuBar.addMenu("編集(&E)"),
            "searchMenu": menuBar.addMenu("検索(&S)"),
            "templateMenu": menuBar.addMenu("定型文(&T)"),
            "bookmarkMenu": menuBar.addMenu("付箋(&B)"),
            "settingMenu": menuBar.addMenu("設定(&O)"),
            "helpMenu": menuBar.addMenu("ヘルプ(&H)"),
        }

        menu["fileMenu"].addActions(list(_g.qAction["file"].values())[:-2])
        menu["historyMenu"] = menu["fileMenu"].addMenu(
            Icon().History, "最近使用したファイル(&R)"
        )
        menu["historyMenu"].addActions(
            [
                QAction(
                    text=f"&{i+1 if i < 9 else 0}: {filePath}",
                    parent=self,
                    triggered=self.openProjectFileFromHistory(filePath),
                    shortcut=QKeySequence("Ctrl+R") if i == 0 else False,
                )
                for i, filePath in enumerate(
                    list(dict.fromkeys(self.settings["FileHistory"]))[:10]
                )
            ]
        )
        menu["historyMenu"].addSeparator()
        menu["historyMenu"].addAction(
            QAction(
                text="履歴ウィンドウ(&R)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("Shift+Ctrl+R"),
            )
        )
        menu["fileMenu"].addSeparator()
        menu["fileMenu"].addAction(list(_g.qAction["file"].values())[-1])

        menu["editMenu"].addActions(list(_g.qAction["edit"].values()))
        menu["searchMenu"].addActions(list(_g.qAction["search"].values()))
        menu["templateMenu"].addActions(list(_g.qAction["template"].values()))
        menu["bookmarkMenu"].addActions(list(_g.qAction["bookmark"].values()))
        menu["settingMenu"].addActions(list(_g.qAction["setting"].values()))
        menu["helpMenu"].addActions(list(_g.qAction["help"].values()))

    def makeToolBar(self):
        toolBarSettings = self.settings["ToolBar"]
        toolButtonsElements = {
            "NewFile": {"actions": [_g.qAction["file"]["NewFile"]]},
            "OpenFile": {"actions": [_g.qAction["file"]["OpenFile"]]},
            "SaveFile": {"actions": [_g.qAction["file"]["SaveFile"]]},
            "SaveFileAs": {"actions": [_g.qAction["file"]["SaveFileAs"]]},
            "Import": {"actions": [_g.qAction["file"]["Import"]]},
            "Export": {"actions": [_g.qAction["file"]["Export"]]},
            "ProjectSetting": {
                "actions": [_g.qAction["file"]["ProjectSetting"]]
            },
            "Reload": {"actions": [_g.qAction["file"]["Reload"]]},
            "Setting": {"actions": [_g.qAction["setting"]["Setting"]]},
            "Search": {"actions": [_g.qAction["search"]["Search"]]},
            "Replace": {"actions": [_g.qAction["search"]["Replace"]]},
            "Template": {"actions": [_g.qAction["template"]["Template"]]},
            "Bookmark": {"actions": [_g.qAction["bookmark"]["Bookmark"]]},
            "Undo": {"actions": [_g.qAction["edit"]["Undo"]]},
            "Repeat": {"actions": [_g.qAction["edit"]["Repeat"]]},
            "CurrentPlace": {
                "text": "カーソルの現在位置",
                "icon": None,
                "actions": None,
            },
            "HotKeys1": {
                "text": "[Ctrl+O]: 開く  [Ctrl+S]: 上書き保存  "
                "[Ctrl+Shift+S]: 名前をつけて保存  [Ctrl+R]: 最後に使ったファイルを開く（起動直後のみ）",
                "icon": None,
                "actions": None,
            },
            "HotKeys2": {
                "text": "[Enter]: 1行追加(下)  [Ctrl+Enter]: 1行追加(上)  "
                "[Shift+Enter]: 通常改行  [Ctrl+Z]: 取り消し  "
                "[Ctrl+Shift+Z]: 取り消しを戻す  [Ctrl+F]: 検索  [Ctrl+Shift+F]: 置換",
                "icon": None,
                "actions": None,
            },
            "HotKeys3": {
                "text": "[Ctrl+Q][Alt+Q][Alt+<]: 左に移る  "
                "[Ctrl+W][Alt+W][Alt+>]: 右に移る",
                "icon": None,
                "actions": None,
            },
            "Info": {"text": "各機能情報", "icon": None, "actions": None},
            "Kaomoji": {"text": "顔文字", "icon": None, "actions": None},
            "StatusBarMessage": {
                "text": "ステータスバー初期メッセージ",
                "icon": None,
                "actions": None,
            },
            "Clock": {"text": "時計", "icon": None, "actions": None},
            "CountDown": {"text": "カウントダウン", "icon": None, "actions": None},
            "StopWatch": {"text": "ストップウォッチ", "icon": None, "actions": None},
        }
        toolButtonStyle = "TextBesideIcon"  # temporary
        toolButtonStyle = getattr(
            Qt.ToolButtonStyle, f"ToolButton{toolButtonStyle}"
        )
        _g.toolBars = []

        for i, toolBarSetting in toolBarSettings.items():
            area = getattr(
                Qt.ToolBarArea, f'{toolBarSetting["area"]}ToolBarArea'
            )
            self.addToolBarBreak(area)
            toolBar = self.addToolBar(f"ツールバー{i+1}")
            toolBar.setToolButtonStyle(toolButtonStyle)
            self.addToolBar(area, toolBar)

            for name in toolBarSetting["contents"]:
                elements = toolButtonsElements[name]
                if elements["actions"]:
                    toolBar.addActions(elements["actions"])
                else:
                    label = QLabel()
                    if elements["text"]:
                        label.setText(elements["text"])
                        label.setObjectName(name)
                    if elements["icon"]:
                        label.setPixmap(elements["icon"])
                    toolBar.addWidget(label)

            _g.toolBars.append(toolBar)

    def makeQActions(self):
        icon = Icon()
        _g.qAction = {}
        _g.qAction["file"] = {
            "NewFile": QAction(
                icon=icon.NewFile,
                text="新規作成(&N)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("Ctrl+N"),
            ),
            "OpenFile": QAction(
                icon=icon.OpenFile,
                text="ファイルを開く(&O)",
                parent=self,
                triggered=self.openProjectFile,
                shortcut=QKeySequence("Ctrl+O"),
            ),
            "SaveFile": QAction(
                icon=icon.SaveFile,
                text="上書き保存(&S)",
                parent=self,
                triggered=self.saveFile,
                shortcut=QKeySequence("Ctrl+S"),
            ),
            "SaveFileAs": QAction(
                icon=icon.SaveFileAs,
                text="名前をつけて保存(&A)",
                parent=self,
                triggered=self.saveFileAs,
                shortcut=QKeySequence("Ctrl+Shift+S"),
            ),
            "Import": QAction(
                icon=icon.Import,
                text="インポート(&I)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("Ctrl+Shift+I"),
            ),
            "Export": QAction(
                icon=icon.Export,
                text="エクスポート(&E)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("Ctrl+Shift+E"),
            ),
            "ProjectSetting": QAction(
                icon=icon.ProjectSetting,
                text="プロジェクト設定(&F)",
                parent=self,
                triggered=print,
            ),
            "Reload": QAction(
                icon=icon.Refresh,
                text="再読込(&W)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("F5"),
            ),
            "History": QAction(
                icon=icon.History,
                text="最近使用したファイル(&R)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("Ctrl+Shift+R"),
            ),
            "Exit": QAction(
                icon=icon.Close,
                text="終了(&Q)",
                parent=self,
                triggered=self.close,
                shortcut=QKeySequence("Alt+F4"),
            ),
        }
        _g.qAction["edit"] = {
            "Cut": QAction(
                icon=icon.Cut,
                text="カット(&T)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("Ctrl+X"),
            ),
            "Copy": QAction(
                icon=icon.Copy,
                text="コピー(&C)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("Ctrl+C"),
            ),
            "Paste": QAction(
                icon=icon.Paste,
                text="ペースト(&P)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("Ctrl+V"),
            ),
            "SelectAll": QAction(
                icon=icon.SelectAll,
                text="すべて選択(&A)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("Ctrl+A"),
            ),
            "SelectLine": QAction(
                icon=icon.Select,
                text="一行選択(&L)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("Ctrl+L"),
            ),
            "Undo": QAction(
                icon=icon.Undo,
                text="取り消し(&U)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("Ctrl+Z"),
            ),
            "Repeat": QAction(
                icon=icon.Redo,
                text="取り消しを戻す(&R)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("Ctrl+Shift+Z"),
            ),
        }
        _g.qAction["search"] = {
            "Search": QAction(
                icon=icon.Search,
                text="検索(&S)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("Ctrl+F"),
            ),
            "Replace": QAction(
                icon=icon.Replace,
                text="置換(&R)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("Ctrl+Shift+F"),
            ),
        }
        _g.qAction["template"] = {
            "Template": QAction(
                icon=icon.Template,
                text="定型文(&T)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("Ctrl+T"),
            ),
        }
        _g.qAction["bookmark"] = {
            "Bookmark": QAction(
                icon=icon.Bookmark,
                text="付箋(&B)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("Ctrl+B"),
            ),
        }
        _g.qAction["setting"] = {
            "Setting": QAction(
                icon=icon.Setting,
                text="設定(&O)",
                parent=self,
                triggered=self.openSubWindow("SettingWindow"),
                shortcut=QKeySequence("Ctrl+Shift+P"),
            ),
            "ProjectSetting": QAction(
                icon=icon.ProjectSetting,
                text="プロジェクト設定(&F)",
                parent=self,
                triggered=print,
            ),
        }
        _g.qAction["help"] = {
            "Help": QAction(
                icon=icon.Help,
                text="ヘルプ(&H)",
                parent=self,
                triggered=print,
                shortcut=QKeySequence("F1"),
            ),
            "InitialStartupMessage": QAction(
                icon=icon.Play,
                text="初回起動メッセージ(&F)",
                parent=self,
                triggered=print,
            ),
            "About": QAction(
                icon=icon.Info,
                text="SoroEditorについて(&A)",
                parent=self,
                triggered=self.openSubWindow("AboutWindow"),
            ),
            "License": QAction(
                icon=icon.Balance,
                text="ライセンス情報(&L)",
                parent=self,
                triggered=self.openSubWindow("ThirdPartyNoticesWindow"),
            ),
        }

    def makeTextEditor(self):
        _g.textEditor = TextEditor(self)

    def saveFile(self) -> bool:
        if self.currentFilePath:
            ret = DataOperation.saveProjectFile(self.currentFilePath)
        else:
            ret = self.saveFileAs()
        if ret:
            self.latestData
            self.latestData = DataOperation.makeSaveData()
        return ret

    def saveFileAs(self) -> bool:
        filePath = QFileDialog().getSaveFileName(
            self,
            "SoroEditor - 名前をつけて保存",
            os.path.join(os.path.curdir, "noname"),
            "SoroEditor Project File(*.sepf *.sep)",
        )[0]
        if filePath:
            ret = DataOperation.saveProjectFile(filePath)
        else:
            ret = False
        if ret:
            self.currentFilePath
            self.currentFilePath = filePath
            self.setWindowTitle(f"SoroEditor - {filePath}")
        return ret

    def isDataChanged(self) -> bool:
        return self.latestData != DataOperation.makeSaveData()

    def openProjectFile(self, filePath: str = ""):
        if self.isDataChanged():
            messageBox = self.dataChangedAlert()
            ret = messageBox.exec()
            if ret == QMessageBox.StandardButton.Save:
                ret = self.saveFile()
                if not ret:
                    return False
            elif ret == QMessageBox.StandardButton.Discard:
                pass
            elif ret == QMessageBox.StandardButton.Cancel:
                return False
            else:
                return False
        if not filePath:
            filePath = QFileDialog().getOpenFileName(
                self,
                "SoroEditor - 開く",
                os.path.curdir,
                "SoroEditor Project File(*.sepf *.sep);;その他(*.*)",
            )[0]
        if filePath:
            data = DataOperation.openProjectFile(filePath)
            if data:
                DataOperation.setTextInTextBoxes(data)
                self.currentFilePath = filePath
                self.latestData = data
                return True
            else:
                return False
        return False

    def openProjectFileFromHistory(self, filePath: str = ""):
        def inner():
            return self.openProjectFile(filePath)

        return inner

    def dataChangedAlert(self) -> QMessageBox:
        messageBox = QMessageBox(self)
        messageBox.setIcon(QMessageBox.Icon.Question)
        messageBox.setWindowTitle("SoroEditor - 終了")
        messageBox.setText("保存されていない変更があります\n閉じる前に保存しますか")
        messageBox.setStandardButtons(
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel
        )
        messageBox.setButtonText(QMessageBox.StandardButton.Save, "保存(&Y)")
        messageBox.setButtonText(
            QMessageBox.StandardButton.Discard, "保存しない(&N)"
        )
        messageBox.setButtonText(
            QMessageBox.StandardButton.Cancel, "キャンセル(&C)"
        )
        messageBox.setDefaultButton(QMessageBox.StandardButton.Save)
        return messageBox

    def setCurrentPlaceLabel(self):
        widget = self.focusWidget()
        if widget:
            if type(widget) is PlainTextEdit:
                type_ = "本文"
                index = _g.textEdits.index(widget)
                block = widget.textCursor().blockNumber()
                positionInBlock = widget.textCursor().positionInBlock()
            elif type(widget) is LineEdit:
                type_ = "タイトル"
                index = _g.lineEdits.index(widget)
                block = None
                positionInBlock = widget.cursorPosition()
            else:
                return

            title = _g.lineEdits[index].text()
            for widget in [
                widget
                for toolBar in _g.toolBars
                for widget in toolBar.children()
            ]:
                if widget.objectName() == "CurrentPlace":
                    text = (
                        f'{title if title else f"{index+1}列"} - {type_}: '
                        f'{"" if block is None else f"{block+1}段落"}'
                        f"{positionInBlock+1}文字    "
                    )
                    widget.setText(text)
        else:
            return

    def loop(self):
        title = "SoroEditor - "
        if self.currentFilePath:
            title += self.currentFilePath
        else:
            title += "(無題)"
        if self.isDataChanged():
            title += "(更新)"
        self.setWindowTitle(title)

    def openSettingFile(self):
        settings = SettingOperation.openSettingFile()
        if not settings:
            settings = copy.deepcopy(SettingOperation.DEFAULTSETTINGDATA)
            SettingOperation.makeNewSettingFile()
        return settings

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.isDataChanged():
            messageBox = self.dataChangedAlert()
            ret = messageBox.exec()
            if ret == QMessageBox.StandardButton.Save:
                ret = self.saveFile()
                if not ret:
                    return event.ignore()
            elif ret == QMessageBox.StandardButton.Discard:
                pass
            elif ret == QMessageBox.StandardButton.Cancel:
                return event.ignore()
        return super().closeEvent(event)

    def openSubWindow(self, type_: QWidget):
        self.subWindows = {
            "ThirdPartyNoticesWindow": None,
            "AboutWindow": None,
            "SettingWindow": None,
        }

        subWindow: type[ThirdPartyNoticesWindow | AboutWindow | SettingWindow]
        if type_ == "ThirdPartyNoticesWindow":
            subWindow = ThirdPartyNoticesWindow
        elif type_ == "AboutWindow":
            subWindow = AboutWindow
        elif type_ == "SettingWindow":
            subWindow = SettingWindow
        else:
            return

        def inner():
            self.subWindows[type_] = subWindow(self)
            self.subWindows[type_].show()

        return inner


class TextEditor(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.makeLayout()

    def makeLayout(self):
        _g.textEdits = [PlainTextEdit() for _ in range(3)]  # temporary
        _g.lineEdits = [LineEdit() for _ in range(3)]  # temporary
        _g.textBoxStretches = [15, 60, 25]  # temporary

        for textEdit in _g.textEdits:
            textEdit.verticalScrollBar().valueChanged.connect(
                self.textBoxScrollBarValueChanged
            )
            textEdit.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            textEdit.cursorPositionChanged.connect(self.cursorPositionChanged)
            textEdit.focusReceived.connect(self.focusReceived)
            textEdit.setTabChangesFocus(True)
        for lineEdit in _g.lineEdits:
            lineEdit.cursorPositionChanged.connect(self.cursorPositionChanged)
            lineEdit.focusReceived.connect(self.focusReceived)

        self.mainScrollBar = QScrollBar()
        self.mainScrollBar.valueChanged.connect(self.mainScrollBarValueChanged)
        self.mainScrollBar.setRange(
            0,
            max(
                [
                    textBox.verticalScrollBar().maximum()
                    for textBox in _g.textEdits
                ]
            ),
        )
        self.mainScrollBar.setPageStep(
            max(
                [
                    textBox.verticalScrollBar().pageStep()
                    for textBox in _g.textEdits
                ]
            )
        )

        self.hlayout = QtWidgets.QHBoxLayout(self)
        self.vlayouts = [
            QtWidgets.QVBoxLayout() for _ in range(len(_g.textEdits))
        ]

        for vlayout, lineEdit, textEdit, stretch in zip(
            self.vlayouts, _g.lineEdits, _g.textEdits, _g.textBoxStretches
        ):
            vlayout.addWidget(lineEdit)
            vlayout.addWidget(textEdit)
            self.hlayout.addLayout(vlayout, stretch)

        for t0, t1 in zip(
            _g.textEdits, (_g.textEdits[1:] + _g.textEdits[:1])[:-1]
        ):
            self.parent.setTabOrder(t0, t1)
        for t0, t1 in zip(
            _g.lineEdits, (_g.lineEdits[1:] + _g.lineEdits[:1])[:-1]
        ):
            self.parent.setTabOrder(t0, t1)

        self.hlayout.addWidget(self.mainScrollBar)

        self.addReturn()
        self.moveToTop()

    def moveToTop(self):
        for textBox in _g.textEdits:
            textBox.verticalScrollBar().setValue(0)
            cursor = QTextCursor(textBox.firstVisibleBlock())
            textBox.setTextCursor(cursor)
            textBox.textCursor()

    def addReturn(self):
        for textBox in _g.textEdits:
            while (
                textBox.verticalScrollBar().maximum()
                <= textBox.verticalScrollBar().pageStep()
            ):
                textBox.appendPlainText("\n")
                textBox.verticalScrollBar().setValue(0)
            while (
                textBox.verticalScrollBar().maximum()
                == textBox.verticalScrollBar().value()
            ):
                textBox.verticalScrollBar().setValue(
                    textBox.verticalScrollBar().maximum() - 2
                )
                textBox.appendPlainText("\n")
                textBox.verticalScrollBar().setValue(
                    textBox.verticalScrollBar().maximum() - 2
                )

    @QtCore.Slot()
    def textChanged(self):
        return

    @QtCore.Slot()
    def textBoxScrollBarValueChanged(self):
        self.addReturn()

        newValue = self.sender().value()
        maxMaximum = max(
            [textBox.verticalScrollBar().maximum() for textBox in _g.textEdits]
        )
        pageStep = max(
            [
                textBox.verticalScrollBar().pageStep()
                for textBox in _g.textEdits
            ]
        )

        self.mainScrollBar.setRange(0, maxMaximum)
        self.mainScrollBar.setValue(newValue)
        self.mainScrollBar.setPageStep(pageStep)

    @QtCore.Slot()
    def mainScrollBarValueChanged(self):
        """
        メインスクロールバーの値が変更された際に各テキストボックスのスクロールバーに値を反映する
        """
        value = self.mainScrollBar.value()
        for textBox in _g.textEdits:
            bar = textBox.verticalScrollBar()
            diff = value - bar.maximum()
            if diff > 0:
                textBox.appendPlainText("\n" * diff)
            else:
                textBox.verticalScrollBar().setValue(value)

    @QtCore.Slot()
    def cursorPositionChanged(self):
        self.parent.setCurrentPlaceLabel()

    @QtCore.Slot()
    def focusReceived(self):
        self.parent.setCurrentPlaceLabel()


class PlainTextEdit(QPlainTextEdit):
    focusReceived = QtCore.Signal()

    def focusInEvent(self, event: QFocusEvent) -> None:
        super().focusInEvent(event)
        self.focusReceived.emit()

    def focusNextPrevChild(self, next: bool) -> bool:
        rect = self.cursorRect()
        for textEdit in _g.textEdits:
            newCursor = textEdit.cursorForPosition(rect.topLeft())
            textEdit.setTextCursor(newCursor)
        return super().focusNextPrevChild(next)


class LineEdit(QLineEdit):
    focusReceived = QtCore.Signal()

    def focusInEvent(self, event: QFocusEvent) -> None:
        super().focusInEvent(event)
        self.focusReceived.emit()
