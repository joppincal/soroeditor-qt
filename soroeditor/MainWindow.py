from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QPlainTextEdit, QScrollBar, QToolBar, QToolButton, QWidget
from random import randint

from soroeditor import __global__ as g
from soroeditor import DataGet, DataSave

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowTitle('SoroEditor')

    def makeLayout(self):
        self.makeTextEditor()
        self.makeMenu()
        self.makeToolBar()
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

    def makeToolBar(self):
        toolBarSettings = {0:{'area':'Top', 'names':['NewFile', 'Save', 'SaveAs']}, 1:{'area':'Bottom', 'names':['Setting']}, 2:{'area':'Left', 'names':['Import', 'Export']}, 3:{'area':'Bottom', 'names':['CurrentPlace']}} # temporary
        toolButtonsElements = {
            'NewFile':{'text':'新規作成', 'icon':None, 'action':None},
            'OpenFile':{'text':'ファイルを開く', 'icon':None, 'action':None},
            'Save':{'text':'上書き保存', 'icon':None, 'action':None},
            'SaveAs':{'text':'名前をつけて保存', 'icon':None, 'action':None},
            'Reload':{'text':'再読込', 'icon':None, 'action':None},
            'ProjectSetting':{'text':'プロジェクト設定', 'icon':None, 'action':None},
            'Setting':{'text':'設定', 'icon':None, 'action':None},
            'Search':{'text':'検索', 'icon':None, 'action':None},
            'Replace':{'text':'置換', 'icon':None, 'action':None},
            'Import':{'text':'インポート', 'icon':None, 'action':None},
            'Export':{'text':'エクスポート', 'icon':None, 'action':None},
            'Template':{'text':'定型文', 'icon':None, 'action':None},
            'Bookmark':{'text':'付箋', 'icon':None, 'action':None},
            'Undo':{'text':'取り消し', 'icon':None, 'action':None},
            'Repeat':{'text':'取り消しを戻す', 'icon':None, 'action':None},

            'CurrentPlace':{'text':'カーソルの現在位置', 'icon':None, 'action':None},
            'HotKeys1':{'text':'[Ctrl+O]: 開く  [Ctrl+S]: 上書き保存  [Ctrl+Shift+S]: 名前をつけて保存  [Ctrl+R]: 最後に使ったファイルを開く（起動直後のみ）', 'icon':None, 'action':None},
            'HotKeys2':{'text':'[Enter]: 1行追加(下)  [Ctrl+Enter]: 1行追加(上)  [Shift+Enter]: 通常改行  [Ctrl+Z]: 取り消し  [Ctrl+Shift+Z]: 取り消しを戻す  [Ctrl+F]: 検索  [Ctrl+Shift+F]: 置換', 'icon':None, 'action':None},
            'HotKeys3':{'text':'[Ctrl+Q][Alt+Q][Alt+<]: 左に移る  [Ctrl+W][Alt+W][Alt+>]: 右に移る', 'icon':None, 'action':None},
            'infomation':{'text':'各機能情報', 'icon':None, 'action':None},
            'kaomoji':{'text':'顔文字', 'icon':None, 'action':None},
            'StatusBarMessage':{'text':'ステータスバー初期メッセージ', 'icon':None, 'action':None},
            'Clock':{'text':'時計', 'icon':None, 'action':None},
            'CountDown':{'text':'カウントダウン', 'icon':None, 'action':None},
            'StopWatch':{'text':'ストップウォッチ', 'icon':None, 'action':None},
        }
        toolButtonStyle = 'IconOnly' # temporary
        toolButtonStyle = getattr(Qt.ToolButtonStyle, f'ToolButton{toolButtonStyle}')
        g.toolBars = {}

        for i, toolBarSetting in toolBarSettings.items():
            toolBar = QToolBar()
            toolBar.setToolButtonStyle(toolButtonStyle)
            area = getattr(Qt.ToolBarArea, f'{toolBarSetting["area"]}ToolBarArea')
            self.addToolBarBreak(area)
            self.addToolBar(area, toolBar)

            toolButtons = []
            for name in toolBarSetting['names']:
                elements = toolButtonsElements[name]
                toolButton = QToolButton()
                toolButton.setText(elements['text'])
                if elements['icon']:
                    toolButton.setIcon(elements['icon'])
                if elements['action']:
                    toolButton.addAction(elements['action'])
                toolBar.addWidget(toolButton)
                toolButtons.append(toolButton)

            g.toolBars[i] = {}
            g.toolBars[i]['toolbar'] = toolBar
            g.toolBars[i]['toolbutton'] = toolButtons

    def makeTextEditor(self):
        g.textEditor = TextEditor(self)


class TextEditor(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.makeLayout()

    def makeLayout(self):
        g.textBoxes = [QPlainTextEdit() for _ in range(3)]

        # textboxにテキストを設定(仮)
        for textBox in g.textBoxes:
            text = ''.join([f'{i}'+'a'*randint(1, 100)+'\n' for i in range(randint(1, 30))])[:-1]
            textBox.setPlainText(text)

        # textboxにSlotを設定
        for textBox in g.textBoxes:
            textBox.verticalScrollBar().valueChanged.connect(self.textBoxScrollBarValueChanged)
            textBox.verticalScrollBar().setVisible(False)
            textBox.cursorPositionChanged.connect(self.cursorPositionChanged)

        global mainScrollBar
        mainScrollBar = QScrollBar()
        mainScrollBar.valueChanged.connect(self.mainScrollBarValueChanged)
        mainScrollBar.setRange(0, max([textBox.verticalScrollBar().maximum() for textBox in g.textBoxes]))
        mainScrollBar.setPageStep(max([textBox.verticalScrollBar().pageStep() for textBox in g.textBoxes]))

        self.hlayout = QtWidgets.QHBoxLayout(self)

        for textBox in g.textBoxes:
            self.hlayout.addWidget(textBox)
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
