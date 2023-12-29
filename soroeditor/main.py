import sys

from PySide6 import QtWidgets

from soroeditor import __global__ as g
from soroeditor.MainWindow import MainWindow
from soroeditor.logSetting import logSetting

def main():
    logSetting()
    g.logger.info('===Start Application===')
    app = QtWidgets.QApplication([])
    mainWindow = MainWindow()
    mainWindow.show()
    mainWindow.makeLayout()
    app.exec()
    g.logger.info('===Close Application===')
    sys.exit()
