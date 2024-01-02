from soroeditor import __global__ as g


def writeToFile(data:str, filePath:str):
    try:
        with open(filePath, mode='wt', encoding='utf-8') as f:
            # ファイルに書き込む
            f.write(data)
    except (FileNotFoundError, UnicodeDecodeError) as e:
        errorType = type(e).__name__
        errorMessage = str(e)
        g.logger.error(f"An error of type {errorType} occurred while writing to the file {filePath}: {errorMessage}")
    else:
        g.logger.info(f'Wrote to the file: {filePath}')

def openFile(filePath:str) -> (str | None):
    try:
        with open(filePath, mode='rt', encoding='utf-8') as f:
            f = f.read()
    except (FileNotFoundError, UnicodeDecodeError) as e:
        errorType = type(e).__name__
        errorMessage = str(e)
        g.logger.error(f'An error of type {errorType} occurred while opening the file {filePath}: {errorMessage}')
    else:
        g.logger.info(f'Open the file: {filePath}')
        return f