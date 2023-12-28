import sys
import yaml

from pprint import pprint
from random import randint
from typing import Optional
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QResizeEvent, QWheelEvent
from PySide6.QtWidgets import QPushButton, QTextEdit, QScrollArea, QLabel, QPlainTextEdit, QScrollBar

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

    def makeLayout(self):

        global textBoxes
        textBoxes = [QPlainTextEdit() for _ in range(3)]

        # textboxにテキストを設定(仮)
        for textbox in textBoxes:
            text = ''.join([f'{i}'+'a'*randint(1, 100)+'\n' for i in range(randint(1, 30))])[:-1]
            textbox.setPlainText(text)

        # textboxにSlotを設定
        for textbox in textBoxes:
            textbox.verticalScrollBar().valueChanged.connect(self.textBoxScrollBarValueChanged)
            textbox.verticalScrollBar().setVisible(True)

        global mainScrollBar
        mainScrollBar = QScrollBar()
        mainScrollBar.valueChanged.connect(self.mainScrollBarValueChanged)
        mainScrollBar.setRange(0, max([textBox.verticalScrollBar().maximum() for textBox in textBoxes]))
        mainScrollBar.setPageStep(max([textBox.verticalScrollBar().pageStep() for textBox in textBoxes]))

        self.hlayout = QtWidgets.QHBoxLayout(self)

        for textbox in textBoxes:
            self.hlayout.addWidget(textbox)
        self.hlayout.addWidget(mainScrollBar)

        self.addReturn()

    def addReturn(self):
        for textBox in textBoxes:
            while textBox.verticalScrollBar().maximum() <= textBox.verticalScrollBar().pageStep():
                textBox.appendPlainText('\n')
            while textBox.verticalScrollBar().maximum() == textBox.verticalScrollBar().value():
                textBox.verticalScrollBar().setValue(textBox.verticalScrollBar().maximum() - 2)
                textBox.appendPlainText('\n')
                textBox.verticalScrollBar().setValue(textBox.verticalScrollBar().maximum() - 2)

    @QtCore.Slot()
    def textChanged(self):
        return
        for textbox in textBoxes:
            count = textbox.blockCount()
            print(count)
            block = textbox.firstVisibleBlock()
            while block.isValid():
                print(block.text()[:2])
                block = block.next()
            return

    @QtCore.Slot()
    def textBoxScrollBarValueChanged(self):
        self.addReturn()

        newValue = self.sender().value()
        maxMaximum = max([textBox.verticalScrollBar().maximum() for textBox in textBoxes])
        pageStep = max([textBox.verticalScrollBar().pageStep() for textBox in textBoxes])

        mainScrollBar.setRange(0, maxMaximum)
        mainScrollBar.setValue(newValue)
        mainScrollBar.setPageStep(pageStep)

    @QtCore.Slot()
    def mainScrollBarValueChanged(self):
        '''
        メインスクロールバーの値が変更された際に各テキストボックスのスクロールバーに値を反映する
        '''
        value = mainScrollBar.value()
        for textBox in textBoxes:
            bar = textBox.verticalScrollBar()
            diff = value - bar.maximum()
            if diff > 0:
                textBox.appendPlainText('\n'*diff)
            else:
                textBox.verticalScrollBar().setValue(value)

    @QtCore.Slot()
    def cursorPositionChanged(self):
        return


class DataGetClass:
    def getCurrentText(self, i:int):
        '''
        numにて指定するテキストボックスのテキストを返す
        対応するテキストボックスが存在しない場合Noneを返す
        '''
        return textBoxes[i].toPlainText() if len(textBoxes) > i else None

    def getAllCurrentText(self):
        '''
        すべてのテキストボックスのテキストをリストで返す
        '''
        return [self.getCurrentText(i) for i in range(len(textBoxes))]


class DataSaveClass:
    def makeSaveData(self):
        return {i: text for i, text in enumerate(DataGetClass().getAllCurrentText())}

    def SaveFile(self, data:dict, file_path:str):
        try:
            with open(file_path, mode='wt', encoding='utf-8') as f:
                # ファイルに書き込む
                yaml.safe_dump(data, f, encoding='utf-8', allow_unicode=True)
                # 変更前のデータを更新する（変更検知に用いられる）
                self.data = data
        except (FileNotFoundError, UnicodeDecodeError, yaml.YAMLError) as e:
            error_type = type(e).__name__
            error_message = str(e)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    widget = MainWindow()
    widget.show()
    widget.makeLayout()
    sys.exit(app.exec())
