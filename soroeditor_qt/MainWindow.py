import os
import sys
from pathlib import Path

from darkdetect import isDark
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QGuiApplication, QKeySequence
from PySide6.QtWidgets import QFileDialog, QLabel, QMainWindow, QMessageBox

from . import DataOperation
from . import SettingOperation as _s
from . import __global__ as _g
from .__version__ import __version__
from .AboutWindow import AboutWindow
from .Icon import Icon
from .logSetting import logSetting
from .SearchOperation import Match
from .SearchWindow import SearchWindow
from .SettingWindow import SettingWindow
from .TextEditor import LineEdit, PlainTextEdit, TextEditor
from .ThirdPartyNoticesWindow import ThirdPartyNoticesWindow

logger = logSetting(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # globalSettings: 設定ファイルに保存される設定
        # projectSettings: プロジェクトファイルごとに保存される設定
        settings = self.openSettingFile()
        settings["Version"] = __version__
        _s.setGlobalSettingData(settings)
        _s.writeSettingFile(_s.globalSettingData())
        _s.setProjectSettingData(_s.globalSettingData())

        self.setWindowTitle("SoroEditor")
        self.setWindowIcon(Icon().AppIcon)

        self.makeLayout()

        self.currentFilePath = ""
        self.latestData = DataOperation.makeSaveData()

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.loop)
        self.timer.start()

        self.reflectionSettings("All")
        self.show()

        if len(sys.argv) >= 2:
            projectFilePath = Path(sys.argv[-1]).absolute()
            if projectFilePath.exists():
                self.openProjectFile(projectFilePath.as_posix())

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
            Icon().History, "ファイル履歴(&R)"
        )
        self.setFileHistoryMenu()
        menu["fileMenu"].addSeparator()
        menu["fileMenu"].addAction(list(_g.qAction["file"].values())[-1])

        menu["editMenu"].addActions(list(_g.qAction["edit"].values()))
        menu["searchMenu"].addActions(list(_g.qAction["search"].values()))
        menu["templateMenu"].addActions(list(_g.qAction["template"].values()))
        menu["bookmarkMenu"].addActions(list(_g.qAction["bookmark"].values()))
        menu["settingMenu"].addActions(list(_g.qAction["setting"].values()))
        menu["helpMenu"].addActions(list(_g.qAction["help"].values()))

    def makeToolBar(self):
        toolBarSettings = _s.projectSettingData()["ToolBar"]
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
            "FileHistory": {"actions": [_g.qAction["file"]["History"]]},
            "Exit": {"actions": [_g.qAction["file"]["Exit"]]},
            "Setting": {"actions": [_g.qAction["setting"]["Setting"]]},
            "Search": {"actions": [_g.qAction["search"]["Search"]]},
            "Replace": {"actions": [_g.qAction["search"]["Replace"]]},
            "Template": {"actions": [_g.qAction["template"]["Template"]]},
            "Bookmark": {"actions": [_g.qAction["bookmark"]["Bookmark"]]},
            "Undo": {"actions": [_g.qAction["edit"]["Undo"]]},
            "Redo": {"actions": [_g.qAction["edit"]["Redo"]]},
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
            "CountDown": {
                "text": "カウントダウン",
                "icon": None,
                "actions": None,
            },
            "StopWatch": {
                "text": "ストップウォッチ",
                "icon": None,
                "actions": None,
            },
        }
        toolButtonStyle = "TextBesideIcon"  # temporary
        toolButtonStyle = getattr(
            Qt.ToolButtonStyle, f"ToolButton{toolButtonStyle}"
        )
        _g.toolBars = []

        for toolBarSetting in toolBarSettings.values():
            enable = toolBarSetting["Enable"]
            if type(enable) is not bool:
                enable = False

            area = toolBarSetting["Area"]
            if area not in ("Top", "Bottom", "Left", "Right"):
                area = "Top"
            area = getattr(Qt.ToolBarArea, f"{area}ToolBarArea")

            title = str(toolBarSetting["Title"])

            contents = toolBarSetting["Contents"]
            if type(contents) is not list:
                contents = []

            self.addToolBarBreak(area)
            toolBar = self.addToolBar(f"{title}")
            toolBar.setToolButtonStyle(toolButtonStyle)
            toolBar.setVisible(enable)
            self.addToolBar(area, toolBar)

            for name in contents:
                elements = toolButtonsElements.get(name, {})
                if elements.get("actions", None):
                    toolBar.addActions(elements["actions"])
                else:
                    label = QLabel()
                    if elements.get("text", None):
                        label.setText(elements["text"])
                        label.setObjectName(name)
                    if elements.get("icon", None):
                        label.setPixmap(elements["icon"])
                    toolBar.addWidget(label)

            if isDark():
                colorName = "#2b2b2b"
            else:
                colorName = "#eaeaea"
            toolBar.setStyleSheet(
                f"""
QToolButton {{ border-style: solid; border-radius: 3px }}
QToolButton:hover:!pressed {{ background-color: {colorName} }}"""
            )

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
                triggered=self.openSubWindow("ProjectSettingWindow"),
                shortcut=QKeySequence("Ctrl+Shift+Alt+P"),
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
                text="ファイル履歴(&R)",
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
            "Redo": QAction(
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
                triggered=self.openSubWindow("SearchWindow"),
                shortcut=QKeySequence("Ctrl+F"),
            ),
            "Replace": QAction(
                icon=icon.Replace,
                text="置換(&R)",
                parent=self,
                triggered=self.openSubWindow("ReplaceWindow"),
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
            "ProjectSetting": _g.qAction["file"]["ProjectSetting"],
            "FullScreen": QAction(
                icon=icon.FullScreen,
                text="全画面表示(F)",
                parent=self,
                triggered=self.toggleFullScreenMode,
                shortcut=QKeySequence("F11"),
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
        self.reflectionSettings("Font")

    def saveFile(self) -> bool:
        if self.currentFilePath:
            ret = DataOperation.saveProjectFile(self.currentFilePath)
        else:
            ret = self.saveFileAs()
        if ret:
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
            self.currentFilePath = filePath
            self.addFileHistory(filePath)
            self.setFileHistoryMenu()
            self.latestData = DataOperation.makeSaveData()
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
                DataOperation.setTextInTextBoxes(data["data"])
                self.currentFilePath = filePath
                self.addFileHistory(filePath)
                self.setFileHistoryMenu()

                data["settings"]["Version"] = __version__
                _s.setProjectSettingData(
                    _s.settingVerification(data["settings"])
                )
                self.reflectionSettings("All")

                self.latestData = DataOperation.makeSaveData()
                return True
            else:
                QMessageBox.information(
                    self,
                    "SoroEditor - Infomation",
                    f"ファイル: {filePath} の開始に失敗しました\nプロジェクトファイルを確認してください",
                )
                return False
        return False

    def openProjectFileFromHistory(self, filePath: str = ""):
        def inner():
            ret = self.openProjectFile(filePath)
            if not ret:
                settings = _s.openSettingFile()
                fileHistory = settings["FileHistory"]
                fileHistory.remove(filePath)
                _s.writeSettingFile(settings)
                _s.setGlobalSettingData(settings)
                self.setFileHistoryMenu()
            return ret

        return inner

    def setFileHistoryMenu(self):
        for action in menu["historyMenu"].actions():
            menu["historyMenu"].removeAction(action)
        menu["historyMenu"].addActions(
            [
                QAction(
                    text=f"&{i+1 if i < 9 else 0}: {filePath}",
                    parent=self,
                    triggered=self.openProjectFileFromHistory(filePath),
                    shortcut=QKeySequence("Ctrl+R") if i == 0 else False,
                )
                for i, filePath in enumerate(
                    list(dict.fromkeys(_s.globalSettingData()["FileHistory"]))[
                        :10
                    ]
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

    def addFileHistory(self, filePath: str):
        settings = _s.openSettingFile()
        fileHistory = settings["FileHistory"]
        fileHistory.insert(0, filePath)
        fileHistory = list(dict.fromkeys(fileHistory))
        settings["FileHistory"] = fileHistory
        _s.setGlobalSettingData(settings)
        _s.writeSettingFile(settings)

    def dataChangedAlert(self) -> QMessageBox:
        messageBox = QMessageBox(self)
        messageBox.setIcon(QMessageBox.Icon.Question)
        messageBox.setWindowTitle("SoroEditor - 終了")
        messageBox.setText(
            "保存されていない変更があります\n閉じる前に保存しますか"
        )
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

    def getCurrentPlace(self):
        widget = self.focusWidget()
        if widget:
            if isinstance(widget, PlainTextEdit):
                box = _g.textEdits.index(widget)
                block = widget.textCursor().blockNumber()
                positionInBlock = widget.textCursor().positionInBlock()
            elif isinstance(widget, LineEdit):
                box = _g.lineEdits.index(widget)
                block = None
                positionInBlock = widget.cursorPosition()
            else:
                return
            return box, block, positionInBlock

    def setCurrentPlaceLabel(self):
        ret = self.getCurrentPlace()
        if ret:
            box, block, positionInBlock = ret

            title = _g.lineEdits[box].text()
            for widget in [
                widget
                for toolBar in _g.toolBars
                for widget in toolBar.children()
            ]:
                if widget.objectName() == "CurrentPlace":
                    text = (
                        f"{title if title else f"ボックス{box+1}"}"
                        ": "
                        f"{"" if block is None else f"{block+1}段落"} "
                        f"{positionInBlock+1}文字"
                        "    "
                    )
                    widget.setText(text)
        else:
            return

    def search(self, pattern, regex):
        return [textEdit.search(pattern, regex) for textEdit in _g.textEdits]

    def replace(self, match: Match, repl: str):
        textEdit = _g.textEdits[match.box]
        textEdit.replace(match, repl)

    def replaceAll(self, matches: list[Match], repl: str, box: int):
        _g.textEdits[box].replaceAll(matches, repl)

    def highlightMatches(self, matches: list[Match], box: int):
        _g.textEdits[box].highlightMatches(matches)

    def focus(self, match: Match):
        for textEdit in _g.textEdits:
            cursor = textEdit.textCursor()
            cursor.clearSelection()
            textEdit.setTextCursor(cursor)
        _g.textEdits[match.box].focus(match)

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
        settings = _s.openSettingFile()
        if not settings:
            settings = _s.defaultSettingData()
            _s.makeNewSettingFile()
        return _s.settingVerification(settings)

    def reflectionSettings(self, item: str):
        """Reflects the settings entered for the item.

        Args:
            item (str): Size, FontFamily, FontSize, ToolBar, All
        """
        settingsMapping = {
            "Size": self.reflectSize,
            "Resizable": self.reflectResizable,
            "FontFamily": self.reflectFontFamily,
            "FontSize": self.reflectFontSize,
            "ToolBar": self.reflectToolBar,
            "All": [
                self.reflectSize,
                self.reflectResizable,
                self.reflectFontFamily,
                self.reflectFontSize,
                self.reflectToolBar,
            ],
        }

        settingFunctions = settingsMapping.get(item)
        if settingFunctions is not None:
            if not isinstance(settingFunctions, list):
                settingFunctions = [settingFunctions]
            for function in settingFunctions:
                function()

    def reflectSize(self):
        size = _s.projectSettingData().get("Size")
        ratio = QGuiApplication.primaryScreen().devicePixelRatio()
        screenSize = QGuiApplication.primaryScreen().size().toTuple()
        if size:
            if type(size) is list:
                self.resize(*[int(lengh / ratio) for lengh in size])
            else:
                self.resize(
                    *[int(lengh / ratio * 0.6) for lengh in screenSize]
                )

            if size in ("Maximize", "FullScreen"):
                self.showMaximized()
                if size == "FullScreen":
                    self.toggleFullScreenMode()
            else:
                self.moveWindowToCenter()

    def reflectResizable(self):
        resizable = _s.projectSettingData().get("Resizable")
        if resizable:
            self.setFixedSize(0xFFFFFF, 0xFFFFFF)
        else:
            self.setFixedSize(self.size())

    def reflectFontFamily(self):
        fontFamily = _s.projectSettingData().get("Font")
        fontStyle = _s.projectSettingData().get("FontStyle")
        if fontFamily:
            font = _g.textEditor.font()
            font.setFamily(fontFamily)
            font.setStyleName(fontStyle)
            _g.textEditor.setFont(font)

    def reflectFontSize(self):
        fontSize = _s.projectSettingData().get("FontSize")
        if fontSize:
            font = _g.textEditor.font()
            font.setPointSize(fontSize)
            _g.textEditor.setFont(font)

    def reflectToolBar(self):
        for toolBar in _g.toolBars:
            self.removeToolBar(toolBar)
        self.makeToolBar()

    def toggleFullScreenMode(self):
        if self.isFullScreen():
            self.showNormal()
            if _s.projectSettingData()["Size"] == "FullScreen":
                self.resize(*_s.defaultSettingData()["Size"])
                self.moveWindowToCenter()
            else:
                self.reflectionSettings("Size")
        else:
            self.showFullScreen()

    def moveWindowToCenter(self):
        self.move(0, 0)
        screen = self.screen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

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

    def openSubWindow(self, type_: str):
        self.subWindows = {
            "AboutWindow": None,
            "ProjectSettingWindow": None,
            "SearchWindow": None,
            "SettingWindow": None,
            "ThirdPartyNoticesWindow": None,
        }

        subWindow: type[
            AboutWindow
            | SearchWindow
            | SettingWindow
            | ThirdPartyNoticesWindow
        ]
        mode = []
        if type_ == "AboutWindow":
            subWindow = AboutWindow
        elif type_ == "SearchWindow":
            subWindow = SearchWindow
            mode = ["search"]
        elif type_ == "ReplaceWindow":
            type_ = "SearchWindow"
            subWindow = SearchWindow
            mode = ["replace"]
        elif type_ == "ProjectSettingWindow":
            subWindow = SettingWindow
            mode = ["Project"]
        elif type_ == "SettingWindow":
            subWindow = SettingWindow
            mode = ["Default"]
        elif type_ == "ThirdPartyNoticesWindow":
            subWindow = ThirdPartyNoticesWindow
        else:
            return

        def inner():
            if self.subWindows[type_] is None:
                self.subWindows[type_] = subWindow(self, *mode)
                self.subWindows[type_].show()
            else:
                if self.subWindows[type_].isHidden():
                    self.subWindows[type_].show()
                self.subWindows[type_].activateWindow()
                self.subWindows[type_].raise_()

        return inner
