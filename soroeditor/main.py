import sys

from PySide6.QtWidgets import QApplication

from soroeditor import __global__ as __g
from soroeditor.logSetting import logSetting
from soroeditor.MainWindow import MainWindow


def main():
    logSetting()
    __g.logger.info("===Start Application===")
    app = QApplication([])
    MainWindow()
    app.exec()
    __g.logger.info("===Close Application===")
    sys.exit()
