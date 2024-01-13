import sys

from PySide6.QtWidgets import QApplication

from soroeditor import __global__ as g
from soroeditor.MainWindow import MainWindow
from soroeditor.logSetting import logSetting

def main():
    logSetting()
    g.logger.info('===Start Application===')
    app = QApplication([])
    MainWindow()
    app.exec()
    g.logger.info('===Close Application===')
    sys.exit()
