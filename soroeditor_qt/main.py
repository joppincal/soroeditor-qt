import os
import sys

from PySide6.QtWidgets import QApplication

from .logSetting import logSetting
from .MainWindow import MainWindow

logger = logSetting(__name__)


def main():
    logger.info("===Start Application===")
    os.environ["QT_QPA_PLATFORM"] = "windows:fontengine=directwrite"
    app = QApplication([])
    MainWindow()
    app.exec()
    logger.info("===Close Application===")
    sys.exit()
