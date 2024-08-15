import os
import sys

from PySide6.QtWidgets import QApplication

from . import __global__
from .MainWindow import MainWindow

from .logSetting import logSetting

logger = logSetting(__name__)


def main():
    logger.info("===Start Application===")
    os.environ["QT_QPA_PLATFORM"] = "windows:fontengine=directwrite"
    app = QApplication([])
    MainWindow()
    app.exec()
    logger.info("===Close Application===")
    sys.exit()
