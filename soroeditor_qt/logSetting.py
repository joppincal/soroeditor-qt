import os
from logging import DEBUG, Formatter, getLogger, handlers

from soroeditor_qt import __global__ as __g


def logSetting():
    if not os.path.exists("./log"):
        os.mkdir("./log")
    __g.logger = getLogger(__name__)
    __g.logger.setLevel(DEBUG)
    formater = Formatter(
        "{asctime} {name:<21s} {levelname:<8s} {message}", style="{"
    )
    handler = handlers.RotatingFileHandler(
        filename="./log/soroeditor.log",
        encoding="utf-8",
        maxBytes=102400,
        backupCount=10,
    )
    handler.setFormatter(formater)
    __g.logger.addHandler(handler)
