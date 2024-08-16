import re
from itertools import chain
from typing import Literal

from darkdetect import isDark
from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtGui import QColor, QKeyEvent, QPalette
from PySide6.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from . import __global__ as _g
from .SearchOperation import Match


class SearchWindow(QWidget):
    def __init__(
        self, parent: QWidget, mode: Literal["search", "replace"]
    ) -> None:
        self.NO_MATCH_MESSAGE = "一致無し"
        super().__init__(parent, Qt.WindowType.Dialog)
        self.title = "SoroEditor - "

        if mode == "search":
            self.title += "検索"
        else:
            self.title += "置換"
        self.setWindowTitle(self.title)

        self.place = -1
        self.matchesList = self.emptyMatchesList()

        self.initUI(mode)

        self.setFixedHeight(self.sizeHint().height())
        self.setFixedWidth(400)

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.reset)
        self.timer.start()

    def initUI(self, mode):
        hBox = QHBoxLayout(self)
        vBox = QVBoxLayout()
        hBox.addLayout(vBox, 50)
        hBox.addStretch(1)

        vBox.addWidget(QLabel("検索"))

        self.searchInput = Input(placeholderText="検索")

        vBox.addWidget(self.searchInput)

        self.regexCheckBox = QCheckBox("正規表現を用いる(&E)")
        vBox.addWidget(
            self.regexCheckBox, alignment=Qt.AlignmentFlag.AlignRight
        )
        self.regexCheckBox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        vBox.addWidget(self.regexCheckBox)

        self.replaceInput = Input(placeholderText="置換", mode="replace")
        if mode == "replace":
            vBox.addWidget(QLabel("置換"))
            vBox.addWidget(self.replaceInput)

        self.messageLabel = QLabel()
        palette = self.messageLabel.palette()
        self.messageLabelTimer = QTimer(self.messageLabel)
        self.messageLabelTimer.setSingleShot(True)
        self.messageLabelTimer.setInterval(10000)

        r = palette.color(QPalette.ColorRole.Window).red()
        g = palette.color(QPalette.ColorRole.Window).green()
        b = palette.color(QPalette.ColorRole.Window).blue()

        if isDark():
            color = QColor(*[c + 30 for c in [r, g, b]])
        else:
            color = QColor(*[c - 30 for c in [r, g, b]])

        palette.setColor(QPalette.ColorRole.Window, color)
        self.messageLabel.setAutoFillBackground(True)
        self.messageLabel.setPalette(palette)
        vBox.addWidget(self.messageLabel)

        dialogButtonBox = QDialogButtonBox(orientation=Qt.Orientation.Vertical)
        buttons = [
            ("検索(&S)", "searchButtonClicked"),
            ("前へ(&P)", "moveToPreviousButtonClicked"),
            ("次へ(&N)", "moveToNextButtonClicked"),
        ]
        if mode == "replace":
            buttons.extend(
                [
                    ("置換(&R)", "replaceButtonClicked"),
                    ("全て置換(&A)", "replaceAllButtonClicked"),
                ]
            )

        for text, method in buttons:
            button = QPushButton(text)
            dialogButtonBox.addButton(button, QDialogButtonBox.ActionRole)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.clicked.connect(getattr(self, method))

        hBox.addWidget(dialogButtonBox)

        self.searchInput.textChanged.connect(self.validateRegex)
        self.regexCheckBox.checkStateChanged.connect(
            lambda: self.validateRegex(self.searchInput.text())
        )

    def changeWindowTitle(self):
        title = self.title + " "

        if self.place >= 0:
            title += f"{self.place + 1}/"

        if self.searchInput.text():
            title += f"{len(self._getMatches())}件"

        self.setWindowTitle(title)

    def changeMessageText(
        self, text: str, color: str = "", delete: bool = True
    ):
        self.messageLabel.setText(text)
        palette = self.messageLabel.palette()
        if color:
            palette.setColor(QPalette.ColorRole.WindowText, color)
        self.messageLabel.setPalette(palette)
        if delete:
            self.messageLabelTimer.stop()
            self.messageLabelTimer.timeout.connect(
                lambda: (
                    self.messageLabel.setText("")
                    if self.messageLabel.text() == text
                    else False
                )
            )
            self.messageLabelTimer.start()

    def search(self, pattern, regex):
        if not pattern:
            return self.emptyMatchesList()

        return self.parent().search(pattern, regex)

    def replace(self, match: Match, repl: str):
        return self.parent().replace(match, repl)

    def focus(self, match: Match):
        self.parent().focus(match)

    def highlightMatches(self):
        for i, matches in enumerate(self.matchesList):
            self.parent().highlightMatches(matches, i)

    def emptyMatchesList(self):
        return [[] for _ in _g.textEdits]

    def _getMatches(self):
        return list(chain(*self.matchesList))

    def moveToMatch(self, direction):
        if not self.validateRegex(self.searchInput.text()):
            return

        matches = self._getMatches()
        if not self.searchInput.text() or not matches:
            self.changeMessageText(self.NO_MATCH_MESSAGE)
            return

        matchesCount = len(matches)
        if direction > 0:
            self.place = (self.place + direction) % matchesCount
        else:
            self.place = (self.place + direction + matchesCount) % matchesCount

        match = matches[self.place]
        self.focus(match)

        currentPlace = self.parent().getCurrentPlace()
        title = _g.lineEdits[currentPlace[0]].text()
        currentPlace = tuple(i + 1 for i in currentPlace)
        if not title:
            title = f"ブロック{currentPlace[0]}"
        block = f"{currentPlace[1]}段落"
        char = f"{currentPlace[2]}文字"
        self.changeMessageText(f"{match.group} - {f"{title}: {block} {char}"}")

    def moveToNextMatch(self):
        self.moveToMatch(1)

    def moveToPreviousMatch(self):
        self.moveToMatch(-1)

    def replaceFocusedText(self):
        matches = self._getMatches()

        if not self.searchInput.text() or not matches:
            self.changeMessageText(self.NO_MATCH_MESSAGE)
            return

        if len(matches) - 1 < self.place:
            self.place = 0

        repl = self.replaceInput.text()
        match = matches[self.place]

        self.replace(match, repl)

        self.reset()

    def afterReplace(self, moveTo: Literal["next", "previous"] = "next"):
        matches = self._getMatches()

        if len(matches) - 1 < self.place:
            self.place = 0

        if not matches:
            self.changeMessageText(self.NO_MATCH_MESSAGE)
            return

        if moveTo == "next":
            self.focus(matches[self.place])
        if moveTo == "previous":
            self.focus(matches[self.place])
            self.moveToPreviousMatch()

        self.changeMessageText(matches[self.place].group)

    def replaceAll(self):
        repl = self.replaceInput.text()
        for box, match in enumerate(self.matchesList):
            self.parent().replaceAll(match, repl, box)
        self.changeMessageText(f"- 全{len(self._getMatches())}件置換完了")

    def validateRegex(self, text):
        if self.regexCheckBox.isChecked():
            try:
                re.compile(text)
            except re.error:
                self.changeMessageText("* 正規表現に誤りあり", "red", False)

                palette = self.searchInput.palette()
                palette.setColor(QPalette.ColorRole.Text, "red")
                self.searchInput.setPalette(palette)

                return False

        self.changeMessageText("")
        palette = self.messageLabel.palette()
        palette.setColor(
            QPalette.ColorRole.WindowText,
            self.palette().color(QPalette.ColorRole.WindowText),
        )
        self.messageLabel.setPalette(palette)

        palette = self.searchInput.palette()
        palette.setColor(
            QPalette.ColorRole.Text,
            self.palette().color(QPalette.ColorRole.Text),
        )
        self.searchInput.setPalette(palette)

        return True

    def reset(self):
        searchText = self.searchInput.text()
        regex = self.regexCheckBox.isChecked()
        self.matchesList = self.search(searchText, regex)
        if not self._getMatches() or not self.searchInput.text():
            self.place = -1
        self.highlightMatches()
        self.changeWindowTitle()

    def searchButtonClicked(self):
        self.moveToNextMatch()

    def replaceButtonClicked(self):
        if self.place < 0:
            self.moveToNextMatch()
            return
        self.replaceFocusedText()
        self.afterReplace("next")

    def replaceAllButtonClicked(self):
        self.replaceAll()

    def moveToNextButtonClicked(self):
        self.moveToNextMatch()

    def moveToPreviousButtonClicked(self):
        self.moveToPreviousMatch()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        self.searchInput.setText("")
        self.reset()
        self.parent().subWindows["SearchWindow"] = None
        self.deleteLater()


class Input(QLineEdit):
    def __init__(
        self,
        placeholderText="",
        mode: Literal["search", "replace"] = "search",
    ):
        super().__init__(placeholderText=placeholderText)
        self.mode = mode
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if (
            obj == self
            and isinstance(event, QKeyEvent)
            and event.type() == QEvent.Type.KeyPress
        ):
            if (
                event.key() == Qt.Key.Key_Return
                and event.modifiers() & Qt.KeyboardModifier.ShiftModifier
            ):
                if self.mode == "search":
                    self.parent().moveToPreviousMatch()
                    return True
                elif self.mode == "replace":
                    if self.parent().place < 0:
                        self.parent().moveToNextMatch()
                        return True
                    self.parent().replaceFocusedText()
                    self.parent().afterReplace("previous")
                    return True
            elif event.key() == Qt.Key.Key_Return:
                if self.mode == "search":
                    self.parent().moveToNextMatch()
                    return True
                elif self.mode == "replace":
                    if self.parent().place < 0:
                        self.parent().moveToNextMatch()
                        return True
                    self.parent().replaceFocusedText()
                    self.parent().afterReplace("next")
                    return True
        return super().eventFilter(obj, event)
