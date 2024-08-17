from logging import DEBUG, Formatter, Logger, getLogger, handlers
from pathlib import Path

logPath = Path.home() / ".soroeditor" / "log"
logPath.mkdir(parents=True, exist_ok=True)


def logSetting(name: str | None = None) -> Logger:
    logger = getLogger(name)
    logger.setLevel(DEBUG)
    formater = Formatter(
        "{asctime} {name:<30s} {levelname:<8s} {message}", style="{"
    )
    handler = handlers.RotatingFileHandler(
        filename=logPath / "soroeditor.log",
        encoding="utf-8",
        maxBytes=102400,
        backupCount=10,
    )
    handler.setFormatter(formater)
    logger.addHandler(handler)

    return logger
