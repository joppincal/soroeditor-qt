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

from . import __global__ as _g
from .SearchOperation import Match


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
            if lineEdit.style().name() == "windows11":
                lineEdit.setTextMargins(-5, 0, 0, 0)

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

        self.hlayout = QHBoxLayout(self)
        self.vlayouts = [QVBoxLayout() for _ in range(len(_g.textEdits))]

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

    @Slot()
    def textChanged(self):
        return

    @Slot()
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

    @Slot()
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

    @Slot()
    def cursorPositionChanged(self):
        self.parent.setCurrentPlaceLabel()

    @Slot()
    def focusReceived(self):
        self.parent.setCurrentPlaceLabel()


class PlainTextEdit(QPlainTextEdit):
    focusReceived = Signal()

    def __init__(self):
        super().__init__()
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
        for textEdit in _g.textEdits:
            newCursor = textEdit.cursorForPosition(rect.topLeft())
            textEdit.setTextCursor(newCursor)
        return super().focusNextPrevChild(next)

    def boxNumber(self):
        return _g.textEdits.index(self)

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
