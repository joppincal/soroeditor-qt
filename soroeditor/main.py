import sys

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from soroeditor import __global__ as g
from soroeditor.MainWindow import MainWindow
from soroeditor.logSetting import logSetting

def main():
    logSetting()
    g.logger.info('===Start Application===')
    app = QApplication([])
    pixmap = QPixmap('soroeditor/src/splash.png')
    splash = QSplashScreen(pixmap)
    splash.show()
    splash.finish(MainWindow())
    app.exec()
    g.logger.info('===Close Application===')
    sys.exit()
