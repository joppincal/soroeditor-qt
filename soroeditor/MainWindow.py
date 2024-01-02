import os
import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup, QKeySequence
from PySide6.QtWidgets import QFileDialog, QMainWindow, QPlainTextEdit, QScrollBar, QToolBar, QToolButton, QWidget

from soroeditor import DataOperation, __global__ as g

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowTitle('SoroEditor')
        self.makeLayout()
        g.filePath = None
        g.data = None
        if len(sys.argv) >= 2:
            if os.path.isfile(sys.argv[1]):
                sys.argv[1] = os.path.abspath(sys.argv[1]).replace('\\', '/')
                data = DataOperation.openProjectFile(sys.argv[1])
                if type(data) is dict:
                    DataOperation.setTextInTextBoxes(data)
                    g.filePath = sys.argv[1]
                    g.data = data
        if g.filePath:
            self.setWindowTitle('SoroEditor - '+g.filePath)

    def makeLayout(self):
        self.makeQActions()
        self.makeTextEditor()
        self.makeToolBar()
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
        menu['fileMenu'].addActions(list(g.qAction['file'].values()))
        menu['fileMenu'].addMenu('最近使用したファイル(&R)')
        menu['fileMenu'].addSeparator()
        menu['fileMenu'].addAction(QAction(text='終了(&Q)', parent=self, triggered=print, shortcut=QKeySequence('Alt+F4')))
        menu['editMenu'].addActions(list(g.qAction['edit'].values()))
        menu['searchMenu'].addActions(list(g.qAction['search'].values()))
        menu['templateMenu'].addActions(list(g.qAction['template'].values()))
        menu['bookmarkMenu'].addActions(list(g.qAction['bookmark'].values()))
        menu['settingMenu'].addActions(list(g.qAction['setting'].values()))
        menu['helpMenu'].addActions(list(g.qAction['help'].values()))

    def makeToolBar(self):
        toolBarSettings = {0:{'area':'Top', 'names':['NewFile', 'OpenFile', 'Save', 'SaveAs']}, 1:{'area':'Bottom', 'names':['Setting']}, 2:{'area':'Left', 'names':['Import', 'Export']}, 3:{'area':'Bottom', 'names':[]}} # temporary
        toolButtonsElements = {
            'NewFile':{'text':'新規作成', 'icon':None, 'action':g.qAction['file']['NewFile']},
            'OpenFile':{'text':'ファイルを開く', 'icon':None, 'action':g.qAction['file']['OpenFile']},
            'Save':{'text':'上書き保存', 'icon':None, 'action':g.qAction['file']['Save']},
            'SaveAs':{'text':'名前をつけて保存', 'icon':None, 'action':g.qAction['file']['SaveAs']},
            'Import':{'text':'インポート', 'icon':None, 'action':g.qAction['file']['Import']},
            'Export':{'text':'エクスポート', 'icon':None, 'action':g.qAction['file']['Export']},
            'ProjectSetting':{'text':'プロジェクト設定', 'icon':None, 'action':g.qAction['file']['ProjectSetting']},
            'Reload':{'text':'再読込', 'icon':None, 'action':g.qAction['file']['Reload']},
            'Setting':{'text':'設定', 'icon':None, 'action':g.qAction['setting']['Setting']},
            'Search':{'text':'検索', 'icon':None, 'action':g.qAction['search']['Search']},
            'Replace':{'text':'置換', 'icon':None, 'action':g.qAction['search']['Replace']},
            'Template':{'text':'定型文', 'icon':None, 'action':g.qAction['template']['Template']},
            'Bookmark':{'text':'付箋', 'icon':None, 'action':g.qAction['bookmark']['Bookmark']},
            'Undo':{'text':'取り消し', 'icon':None, 'action':g.qAction['edit']['Undo']},
            'Repeat':{'text':'取り消しを戻す', 'icon':None, 'action':g.qAction['edit']['Repeat']},

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
        toolButtonStyle = 'TextOnly' # temporary
        toolButtonStyle = getattr(Qt.ToolButtonStyle, f'ToolButton{toolButtonStyle}')
        g.toolBars = {}

        for i, toolBarSetting in toolBarSettings.items():
            area = getattr(Qt.ToolBarArea, f'{toolBarSetting["area"]}ToolBarArea')
            self.addToolBarBreak(area)
            toolBar = self.addToolBar(f'ツールバー{i+1}')
            toolBar.setToolButtonStyle(toolButtonStyle)
            self.addToolBar(area, toolBar)

            for name in toolBarSetting['names']:
                elements = toolButtonsElements[name]
                toolBar.addAction(elements['action'])

            g.toolBars[i] = {}
            g.toolBars[i]['toolbar'] = toolBar

    def makeQActions(self):
        g.qAction = {}
        g.qAction['file'] = {
            'NewFile': QAction(text='新規作成(&N)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+N')),
            'OpenFile': QAction(text='ファイルを開く(&O)', parent=self, triggered=self.openFile, shortcut=QKeySequence('Ctrl+O')),
            'Save': QAction(text='上書き保存(&S)', parent=self, triggered=self.saveFile, shortcut=QKeySequence('Ctrl+S')),
            'SaveAs': QAction(text='名前をつけて保存(&A)', parent=self, triggered=self.saveFileAs, shortcut=QKeySequence('Ctrl+Shift+S')),
            'Import': QAction(text='インポート(&I)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+Shift+I')),
            'Export': QAction(text='エクスポート(&E)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+Shift+E')),
            'ProjectSetting': QAction(text='プロジェクト設定(&F)', parent=self, triggered=print),
            'Reload': QAction(text='再読込(&W)', parent=self, triggered=print, shortcut=QKeySequence('F5')),
            }
        g.qAction['edit'] = {
            'Cut': QAction(text='カット(&T)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+X')),
            'Copy': QAction(text='コピー(&C)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+C')),
            'Paste': QAction(text='ペースト(&P)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+V')),
            'SelectAll': QAction(text='すべて選択(&A)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+A')),
            'SelectLine': QAction(text='一行選択(&L)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+L')),
            'Undo': QAction(text='取り消し(&U)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+Z')),
            'Repeat': QAction(text='取り消しを戻す(&R)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+Shift+Z')),
            }
        g.qAction['search'] = {
            'Search': QAction(text='検索(&S)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+F')),
            'Replace': QAction(text='置換(&R)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+Shift+F')),
            }
        g.qAction['template'] = {
            'Template': QAction(text='定型文(&T)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+T')),
            }
        g.qAction['bookmark'] = {
            'Bookmark': QAction(text='付箋(&B)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+B')),
            }
        g.qAction['setting'] = {
            'Setting': QAction(text='設定(&O)', parent=self, triggered=print, shortcut=QKeySequence('Ctrl+Shift+P')),
            'ProjectSetting': QAction(text='プロジェクト設定(&F)', parent=self, triggered=print),
            }
        g.qAction['help'] = {
            'Help': QAction(text='ヘルプ(&H)', parent=self, triggered=print, shortcut=QKeySequence('F1')),
            'InitialStartupMessage': QAction(text='初回起動メッセージ(&F)', parent=self, triggered=print),
            'About': QAction(text='SoroEditorについて(&A)', parent=self, triggered=print),
            'License': QAction(text='ライセンス情報(&L)', parent=self, triggered=print),
            }

    def makeTextEditor(self):
        g.textEditor = TextEditor(self)

    def saveFile(self):
        if g.filePath:
            DataOperation.saveProjectFile(g.filePath)
        else:
            self.saveFileAs()

    def saveFileAs(self):
        filePath = QFileDialog().getSaveFileName(
            self,
            'SoroEditor - 名前をつけて保存',
            os.path.join(os.path.curdir, 'noname'),
            'SoroEditor Project File(*.sepf *.sep)',
            )[0]
        if filePath:
            DataOperation.saveProjectFile(filePath)

    def openFile(self):
        filePath = QFileDialog().getOpenFileName(
            self,
            'SoroEditor - 開く',
            os.path.curdir,
            'SoroEditor Project File(*.sepf *.sep);;その他(*.*)'
            )[0]
        if filePath:
            data = DataOperation.openProjectFile(filePath)
            DataOperation.setTextInTextBoxes(data)
            self.setWindowTitle('SoroEditor - '+filePath)


class TextEditor(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.makeLayout()

    def makeLayout(self):
        g.textBoxes = [QPlainTextEdit() for _ in range(3)]

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
