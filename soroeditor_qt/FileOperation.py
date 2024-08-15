from .logSetting import logSetting

logger = logSetting(__name__)


def writeToFile(data: str, filePath: str) -> bool:
    try:
        with open(filePath, mode="wt", encoding="utf-8") as f:
            # ファイルに書き込む
            f.write(data)
    except (FileNotFoundError, UnicodeDecodeError) as e:
        errorType = type(e).__name__
        errorMessage = str(e)
        logger.error(
            f"An error of type {errorType} occurred while writing to the file "
            f"{filePath}: {errorMessage}"
        )
        return False
    else:
        logger.info(f"Wrote to the file: {filePath}")
        return True


def openFile(filePath: str) -> str | None:
    try:
        with open(filePath, mode="rt", encoding="utf-8") as f:
            str_ = f.read()
    except (FileNotFoundError, UnicodeDecodeError) as e:
        errorType = type(e).__name__
        errorMessage = str(e)
        logger.error(
            f"An error of type {errorType} occurred while opening the file "
            f"{filePath}: {errorMessage}"
        )
        return None
    else:
        logger.info(f"Open the file: {filePath}")
        return str_
