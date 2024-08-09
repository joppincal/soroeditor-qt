import os
import sys

from PySide6.QtWidgets import QApplication

from soroeditor_qt import __global__ as __g
from soroeditor_qt.logSetting import logSetting
from soroeditor_qt.MainWindow import MainWindow


def main():
    logSetting()
    __g.logger.info("===Start Application===")
    os.environ["QT_QPA_PLATFORM"] = "windows:fontengine=directwrite"
    app = QApplication([])
    MainWindow()
    app.exec()
    __g.logger.info("===Close Application===")
    sys.exit()
