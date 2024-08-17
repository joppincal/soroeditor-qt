import re

from darkdetect import isDark
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFocusEvent, QPalette, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPlainTextEdit,
    QScrollBar,
    QVBoxLayout,
    QWidget,
)

from .SearchOperation import Match


class TextEditor(QWidget):
    def __init__(
        self,
        parent: QWidget,
        numberOfBoxes: int = 3,
        boxStretches: list[int] = [15, 60, 25],
    ):
        super().__init__(parent)
        self.textEdits = [PlainTextEdit() for _ in range(numberOfBoxes)]
        self.lineEdits = [LineEdit() for _ in range(numberOfBoxes)]
        self.boxStretches = boxStretches
        self.makeLayout()

    def makeLayout(self):
        for textEdit in self.textEdits:
            textEdit.verticalScrollBar().valueChanged.connect(
                self.textBoxScrollBarValueChanged
            )
            textEdit.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

            textEdit.cursorPositionChanged.connect(self.cursorPositionChanged)
            textEdit.focusReceived.connect(self.focusReceived)
            textEdit.setTabChangesFocus(True)
        for lineEdit in self.lineEdits:
            lineEdit.cursorPositionChanged.connect(self.cursorPositionChanged)
            lineEdit.focusReceived.connect(self.focusReceived)
            if lineEdit.style().name() == "windows11":
                lineEdit.setTextMargins(-5, 0, 0, 0)

        self.mainScrollBar = QScrollBar()
        self.mainScrollBar.valueChanged.connect(self.mainScrollBarValueChanged)
        self.mainScrollBar.setRange(
            0,
            max(
                [
                    textEdit.verticalScrollBar().maximum()
                    for textEdit in self.textEdits
                ]
            ),
        )
        self.mainScrollBar.setPageStep(
            max(
                [
                    textEdit.verticalScrollBar().pageStep()
                    for textEdit in self.textEdits
                ]
            )
        )

        self.hlayout = QHBoxLayout(self)
        self.vlayouts = [QVBoxLayout() for _ in range(len(self.textEdits))]

        for vlayout, lineEdit, textEdit, stretch in zip(
            self.vlayouts,
            self.lineEdits,
            self.textEdits,
            self.boxStretches,
        ):
            vlayout.addWidget(lineEdit)
            vlayout.addWidget(textEdit)
            self.hlayout.addLayout(vlayout, stretch)

        for t0, t1 in zip(
            self.textEdits, (self.textEdits[1:] + self.textEdits[:1])[:-1]
        ):
            self.parent().setTabOrder(t0, t1)
        for t0, t1 in zip(
            self.lineEdits, (self.lineEdits[1:] + self.lineEdits[:1])[:-1]
        ):
            self.parent().setTabOrder(t0, t1)

        self.hlayout.addWidget(self.mainScrollBar)

        self.addReturn()
        self.moveToTop()

    def moveToTop(self):
        for textEdit in self.textEdits:
            textEdit.verticalScrollBar().setValue(0)
            cursor = QTextCursor(textEdit.firstVisibleBlock())
            textEdit.setTextCursor(cursor)
            textEdit.textCursor()

    def addReturn(self):
        for textEdit in self.textEdits:
            while (
                textEdit.verticalScrollBar().maximum()
                <= textEdit.verticalScrollBar().pageStep()
            ):
                textEdit.appendPlainText("\n")
                textEdit.verticalScrollBar().setValue(0)
            while (
                textEdit.verticalScrollBar().maximum()
                == textEdit.verticalScrollBar().value()
            ):
                textEdit.verticalScrollBar().setValue(
                    textEdit.verticalScrollBar().maximum() - 2
                )
                textEdit.appendPlainText("\n")
                textEdit.verticalScrollBar().setValue(
                    textEdit.verticalScrollBar().maximum() - 2
                )

    @Slot()
    def textChanged(self):
        return

    @Slot()
    def textBoxScrollBarValueChanged(self):
        self.addReturn()

        newValue = self.sender().value()
        maxMaximum = max(
            [
                textEdit.verticalScrollBar().maximum()
                for textEdit in self.textEdits
            ]
        )
        pageStep = max(
            [
                textEdit.verticalScrollBar().pageStep()
                for textEdit in self.textEdits
            ]
        )

        self.mainScrollBar.setRange(0, maxMaximum)
        self.mainScrollBar.setValue(newValue)
        self.mainScrollBar.setPageStep(pageStep)

    @Slot()
    def mainScrollBarValueChanged(self):
        """
        メインスクロールバーの値が変更された際に各テキストボックスのスクロールバーに値を反映する
        """
        value = self.mainScrollBar.value()
        for textEdit in self.textEdits:
            bar = textEdit.verticalScrollBar()
            diff = value - bar.maximum()
            if diff > 0:
                textEdit.appendPlainText("\n" * diff)
            else:
                textEdit.verticalScrollBar().setValue(value)

    @Slot()
    def cursorPositionChanged(self):
        self.parent().setCurrentPlaceLabel()

    @Slot()
    def focusReceived(self):
        self.parent().setCurrentPlaceLabel()

    def getCurrentText(self, i: int) -> str | None:
        """
        numにて指定するテキストボックスのテキストを返す
        対応するテキストボックスが存在しない場合Noneを返す
        """
        return (
            self.textEdits[i].toPlainText()
            if len(self.textEdits) > i
            else None
        )

    def getCurrentTitle(self, i: int) -> str | None:
        """
        numにて指定するテキストボックスのタイトルを返す
        対応するラインエディットが存在しない場合Noneを返す
        """
        return self.lineEdits[i].text() if len(self.lineEdits) > i else None

    def getAllCurrentText(self) -> list[str | None]:
        """
        すべてのテキストボックスのテキストをリストで返す
        """
        return [self.getCurrentText(i) for i in range(len(self.textEdits))]

    def getAllCurrentTitle(self) -> list[str | None]:
        """
        すべてのラインエディットのテキストをリストで返す
        """
        return [self.getCurrentTitle(i) for i in range(len(self.lineEdits))]

    def setTextInTextBoxes(self, dic: dict):
        numberOfTextBoxes = len(self.textEdits)
        for i in range(100):
            if i not in dic or i >= numberOfTextBoxes:
                pass
                return
            self.textEdits[i].setPlainText(dic[i]["text"])
            self.lineEdits[i].setText(dic[i]["title"])
            self.addReturn()


class PlainTextEdit(QPlainTextEdit):
    focusReceived = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        palette = self.palette()

        # 非アクティブ状態（フォーカスがない場合）の選択色
        highlightColor = palette.color(QPalette.ColorRole.Highlight)
        highlightColor.setAlphaF(0.7)
        palette.setColor(QPalette.Inactive, QPalette.Highlight, highlightColor)
        highlightedTextColor = palette.color(
            QPalette.ColorRole.HighlightedText
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.HighlightedText,
            highlightedTextColor,
        )

        self.setPalette(palette)

    def focusInEvent(self, event: QFocusEvent) -> None:
        super().focusInEvent(event)
        self.focusReceived.emit()

    def focusNextPrevChild(self, next: bool) -> bool:
        rect = self.cursorRect()
        for textEdit in self.parent().textEdits:
            newCursor = textEdit.cursorForPosition(rect.topLeft())
            textEdit.setTextCursor(newCursor)
        return super().focusNextPrevChild(next)

    def boxNumber(self):
        return self.parent().textEdits.index(self)

    def replace(self, match: Match, repl: str):
        document = self.document()
        cursor = QTextCursor(document)
        cursor.setPosition(match.start)
        cursor.setPosition(match.end, QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(repl)

    def replaceAll(self, matches: list[Match], repl: str):
        document = self.document()
        cursors: list[QTextCursor] = []
        for match in matches:
            cursor = QTextCursor(document)
            cursor.setPosition(match.start)
            cursor.setPosition(match.end, QTextCursor.MoveMode.KeepAnchor)
            cursors.append(cursor)

        for cursor in cursors:
            cursor.insertText(repl)

    def findMatches(self, string, pattern, regex):
        box = self.boxNumber()
        matches = []
        if regex:
            try:
                pattern = re.compile(pattern)
                for match in pattern.finditer(string):
                    matches.append(
                        Match(match.start(), match.end(), match.group(), box)
                    )
            except re.error:
                return []
        else:
            start = 0
            while True:
                index = string.find(pattern, start)
                if index == -1:
                    break
                matches.append(
                    Match(index, index + len(pattern), pattern, box)
                )
                start = index + 1
        return matches

    def search(self, pattern: str, regex: bool):
        document = self.document()
        string = document.toPlainText()

        # Matchオブジェクトを取得
        return self.findMatches(string, pattern, regex)

    def highlightMatches(self, matches: list[Match]):
        document = self.document()
        highlightFormat = QTextCharFormat()

        # 既存のハイライトを削除
        cursor = QTextCursor(document)
        cursor.beginEditBlock()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(QTextCharFormat())
        cursor.endEditBlock()

        highlightColor = self.palette().color(QPalette.ColorRole.Window)
        if isDark():
            highlightColor.setRgbF(0.4, 0.4, 0.4, 1.0)
        else:
            highlightColor.setRgbF(0.6, 0.6, 0.6, 1.0)
        highlightFormat.setBackground(highlightColor)

        for match in matches:
            cursor = QTextCursor(document)
            cursor.setPosition(match.start)
            cursor.setPosition(match.end, QTextCursor.MoveMode.KeepAnchor)
            cursor.mergeCharFormat(highlightFormat)

    def focus(self, match: Match):
        self.setFocus()
        document = self.document()
        cursor = QTextCursor(document)
        cursor.setPosition(match.start)
        cursor.setPosition(match.end, QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()


class LineEdit(QLineEdit):
    focusReceived = Signal()

    def focusInEvent(self, event: QFocusEvent) -> None:
        super().focusInEvent(event)
        self.focusReceived.emit()
