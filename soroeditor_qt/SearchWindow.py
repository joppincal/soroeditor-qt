import re
from typing import Literal
from itertools import chain

from darkdetect import isDark
from PySide6.QtCore import Slot, Qt, QTimer, QEvent
from PySide6.QtGui import QColor, QPalette, QKeyEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QLabel,
    QSizePolicy,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .SearchOperation import Match


class SearchWindow(QWidget):
    def __init__(
        self, parent: QWidget, mode: Literal["Search", "Replace"]
    ) -> None:
        super().__init__(parent, Qt.WindowType.Dialog)
        self.title = "SoroEditor - "

        if mode == "Search":
            self.title += "検索"
        else:
            self.title += "置換"
        self.setWindowTitle(self.title)

        self.place = -1
        self.matchesList = []

        self.initUI(mode)

        self.setMinimumWidth(300)
        self.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Maximum
        )

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.reset)
        self.timer.start()

    def initUI(self, mode):
        vBox = QVBoxLayout(self)

        vBox.addWidget(QLabel("検索"))

        self.searchInput = Input(self, placeholderText="検索")
        self.searchInput.setPlaceholderText("検索")

        vBox.addWidget(self.searchInput)

        self.regexCheckBox = QCheckBox("正規表現を用いる")
        vBox.addWidget(
            self.regexCheckBox, alignment=Qt.AlignmentFlag.AlignRight
        )
        vBox.addWidget(self.regexCheckBox)

        self.replaceInput = QLineEdit(placeholderText="置換")
        if mode == "Replace":
            vBox.addWidget(QLabel("置換"))
            vBox.addWidget(self.replaceInput)

        self.messageLabel = QLabel()
        palette = self.messageLabel.palette()

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

        dialogButtonBox = QDialogButtonBox()
        if mode == "Search":
            dialogButton = QDialogButtonBox.StandardButton.Apply
        else:
            dialogButton = (
                QDialogButtonBox.StandardButton.Apply
                | QDialogButtonBox.StandardButton.Save
                | QDialogButtonBox.StandardButton.SaveAll
            )
        dialogButtonBox.setStandardButtons(dialogButton)

        dialogButtonBox.button(QDialogButtonBox.StandardButton.Apply).setText(
            "検索(S)"
        )
        dialogButtonBox.button(
            QDialogButtonBox.StandardButton.Apply
        ).setDefault(True)
        if mode == "Replace":
            dialogButtonBox.button(
                QDialogButtonBox.StandardButton.Save
            ).setText("置換(R)")
            dialogButtonBox.button(
                QDialogButtonBox.StandardButton.SaveAll
            ).setText("全て置換(A)")
        vBox.addWidget(dialogButtonBox)

        # self.searchInput.returnPressed.connect(self.searchButtonClicked)
        self.replaceInput.returnPressed.connect(self.replaceButtonClicked)
        dialogButtonBox.clicked.connect(self.clicked)

    def changeWindowTitle(self):
        title = self.title + " "

        if self.place >= 0:
            title += f"{self.place + 1}/"

        if self.searchInput.text():
            title += f"{len(list(chain(*self.matchesList)))}件"

        self.setWindowTitle(title)

    def search(self, pattern, regex):
        if regex:
            try:
                re.compile(pattern)
            except re.error:
                self.messageLabel.setText("* 正規表現に誤りあり")
                return []
            else:
                if self.messageLabel.text() == "* 正規表現に誤りあり":
                    self.messageLabel.setText("")
        else:
            if self.messageLabel.text() == "* 正規表現に誤りあり":
                self.messageLabel.setText("")

        if not pattern:
            return []

        return self.parent().search(pattern, regex)

    def replace(self, match: Match, repl: str):
        return self.parent().replace(match, repl)

    def focus(self, match: Match):
        self.parent().focus(match)

    def highlightMatches(self):
        for i, matches in enumerate(self.matchesList):
            self.parent().highlightMatches(matches, i)

    def moveToNextMatch(self):
        matches = list(chain(*self.matchesList))

        if not self.searchInput.text() or not matches:
            self.messageLabel.setText("一致無し")
            return

        self.place += 1

        if len(matches) - 1 < self.place:
            self.place = 0

        self.focus(matches[self.place])
        self.messageLabel.setText(matches[self.place].group)

    def moveToPreviousMatch(self):
        matches = list(chain(*self.matchesList))

        if not self.searchInput.text() or not matches:
            self.messageLabel.setText("一致無し")
            return

        self.place -= 1

        if self.place < 0:
            self.place = len(matches) - 1

        self.focus(matches[self.place])
        self.messageLabel.setText(matches[self.place].group)

    def replacefocusedText(self):
        matches = list(chain(*self.matchesList))

        if len(matches) - 1 < self.place:
            self.place = 0

        repl = self.replaceInput.text()
        match = matches[self.place]

        self.replace(match, repl)

        self.reset()

        matches = list(chain(*self.matchesList))

        if len(matches) - 1 < self.place:
            self.place = 0

        if not matches:
            self.messageLabel.setText("一致無し")
            return

        self.focus(matches[self.place])
        self.messageLabel.setText(matches[self.place].group)

    def replaceAll(self):
        repl = self.replaceInput.text()
        for box, match in enumerate(self.matchesList):
            self.parent().replaceAll(match, repl, box)
        self.messageLabel.setText(
            f"- 全{len(list(chain(*self.matchesList)))}件置換完了"
        )

    def reset(self):
        searchText = self.searchInput.text()
        regex = self.regexCheckBox.isChecked()
        self.matchesList = self.search(searchText, regex)
        if not list(chain(*self.matchesList)) or not self.searchInput.text():
            self.place = -1
        self.highlightMatches()
        self.changeWindowTitle()

    @Slot(QPushButton)
    def clicked(self, button: QPushButton):
        buttonText = button.text()

        if "(S)" in buttonText:
            # マッチ地点に順に移動
            self.searchButtonClicked()
        elif "(R)" in buttonText:
            # マッチ地点に順に移動・置換
            self.replaceButtonClicked()
        elif "(A)" in buttonText:
            # マッチ地点を全て置換
            self.replaceAllButtonClicked()

    def searchButtonClicked(self):
        self.moveToNextMatch()

    def replaceButtonClicked(self):
        if self.place < 0:
            self.moveToNextMatch()
            return
        self.replacefocusedText()

    def replaceAllButtonClicked(self):
        self.replaceAll()

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
    def __init__(self, parent=None, placeholderText=""):
        super().__init__(parent, placeholderText=placeholderText)
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
                self.parent().moveToPreviousMatch()
                return True
            elif event.key() == Qt.Key.Key_Return:
                self.parent().moveToNextMatch()
                return True
        return super().eventFilter(obj, event)
