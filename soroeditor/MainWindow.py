from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QPlainTextEdit, QScrollBar, QWidget, QMainWindow
from random import randint

from soroeditor import __global__ as g

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowTitle('SoroEditor')

    def makeLayout(self):
        self.makeTextEditor()
        self.makeMenu()
        self.setCentralWidget(g.textEditor)

    def makeMenu(self):
        menuBar = self.menuBar()
        global menu
        menu = {
            'fileMenu':  menuBar.addMenu('ファイル(&F)'),
            'editMenu': menuBar.addMenu('編集(&E)'),
            'searchMenu': menuBar.addMenu('検索(&S)'),
            'templateMenu': menuBar.addMenu('定型文(&T)'),
            'bookmarkMenu': menuBar.addMenu('付箋(&B)'),
            'settingMenu': menuBar.addMenu('設定(&O)'),
            'helpMenu': menuBar.addMenu('ヘルプ(&H)'),
            }
        menu['fileMenu'].addActions(
            [
                QAction(text='新規作成(&N)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+N')),
                QAction(text='ファイルを開く(&O)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+O')),
                QAction(text='上書き保存(&S)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+S')),
                QAction(text='名前をつけて保存(&A)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+Shift+S')),
                QAction(text='インポート(&I)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+Shift+I')),
                QAction(text='エクスポート(&E)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+Shift+E')),
                QAction(text='プロジェクト設定(&F)', parent=self, triggered=print),
                QAction(text='再読込(&W)', parent=self, triggered=print, shortcut=QKeySequence('F5')),
                ]
            )
        menu['fileMenu'].addMenu('最近使用したファイル(&R)')
        menu['fileMenu'].addSeparator()
        menu['fileMenu'].addAction(QAction(text='終了(&Q)', parent=self, triggered=print, shortcut=QKeySequence('Alt+F4')))
        menu['editMenu'].addActions(
            [
                QAction(text='カット(&T)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+X')),
                QAction(text='コピー(&C)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+C')),
                QAction(text='ペースト(&P)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+V')),
                QAction(text='すべて選択(&A)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+A')),
                QAction(text='一行選択(&L)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+L')),
                QAction(text='取り消し(&U)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+Z')),
                QAction(text='取り消しを戻す(&R)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+Shift+Z')),
                ]
            )
        menu['searchMenu'].addActions(
            [
                QAction(text='検索(&S)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+F')),
                QAction(text='置換(&R)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+Shift+F')),
                ]
            )
        menu['templateMenu'].addActions(
            [
                QAction(text='定型文(&T)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+T')),
                ]
            )
        menu['bookmarkMenu'].addActions(
            [
                QAction(text='付箋(&B)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+B')),
                ]
            )
        menu['settingMenu'].addActions(
            [
                QAction(text='設定(&O)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+Shift+P')),
                QAction(text='プロジェクト設定(&F)', parent=self, triggered=print),
                ]
            )
        menu['helpMenu'].addActions(
            [
                QAction(text='ヘルプ(&H)', parent=self, triggered=print, shortcut=QKeySequence('F1')),
                QAction(text='初回起動メッセージを表示(&F)', parent=self, triggered=print),
                QAction(text='SoroEditorについて(&A)', parent=self, triggered=print),
                QAction(text='ライセンス情報(&L)', parent=self, triggered=print),
                ]
            )

    def makeTextEditor(self):
        g.textEditor = TextEditor(self)


class TextEditor(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.makeLayout()

    def makeLayout(self):
        g.textBoxes = [QPlainTextEdit() for _ in range(3)]

        # textboxにテキストを設定(仮)
        for textbox in g.textBoxes:
            text = ''.join([f'{i}'+'a'*randint(1, 100)+'\n' for i in range(randint(1, 30))])[:-1]
            textbox.setPlainText(text)

        # textboxにSlotを設定
        for textbox in g.textBoxes:
            textbox.verticalScrollBar().valueChanged.connect(self.textBoxScrollBarValueChanged)
            textbox.verticalScrollBar().setVisible(False)

        global mainScrollBar
        mainScrollBar = QScrollBar()
        mainScrollBar.valueChanged.connect(self.mainScrollBarValueChanged)
        mainScrollBar.setRange(0, max([textBox.verticalScrollBar().maximum() for textBox in g.textBoxes]))
        mainScrollBar.setPageStep(max([textBox.verticalScrollBar().pageStep() for textBox in g.textBoxes]))

        self.hlayout = QtWidgets.QHBoxLayout(self)

        for textbox in g.textBoxes:
            self.hlayout.addWidget(textbox)
        self.hlayout.addWidget(mainScrollBar)

        self.addReturn()

    def addReturn(self):
        for textBox in g.textBoxes:
            while textBox.verticalScrollBar().maximum() <= textBox.verticalScrollBar().pageStep():
                textBox.appendPlainText('\n')
                textBox.verticalScrollBar().setValue(0)
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
        maxMaximum = max([textBox.verticalScrollBar().maximum() for textBox in g.textBoxes])
        pageStep = max([textBox.verticalScrollBar().pageStep() for textBox in g.textBoxes])

        mainScrollBar.setRange(0, maxMaximum)
        mainScrollBar.setValue(newValue)
        mainScrollBar.setPageStep(pageStep)

    @QtCore.Slot()
    def mainScrollBarValueChanged(self):
        '''
        メインスクロールバーの値が変更された際に各テキストボックスのスクロールバーに値を反映する
        '''
        value = mainScrollBar.value()
        for textBox in g.textBoxes:
            bar = textBox.verticalScrollBar()
            diff = value - bar.maximum()
            if diff > 0:
                textBox.appendPlainText('\n'*diff)
            else:
                textBox.verticalScrollBar().setValue(value)

    @QtCore.Slot()
    def cursorPositionChanged(self):
        return
