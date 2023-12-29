from logging import DEBUG, Formatter, getLogger, handlers
import os

from soroeditor import __global__ as g

def logSetting():
    if not os.path.exists('./log'):
        os.mkdir('./log')
    g.logger = getLogger(__name__)
    g.logger.setLevel(DEBUG)
    formater = Formatter('{asctime} {name:<21s} {levelname:<8s} {message}', style='{')
    handler = handlers.RotatingFileHandler(
        filename='./log/soroeditor.log',
        encoding='utf-8',
        maxBytes=102400,
        backupCount=10)
    handler.setFormatter(formater)
    g.logger.addHandler(handler)
