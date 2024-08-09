import yaml as __y

from soroeditor_qt import FileOperation
from soroeditor_qt import __global__ as __g


def getCurrentText(i: int) -> str | None:
    """
    numにて指定するテキストボックスのテキストを返す
    対応するテキストボックスが存在しない場合Noneを返す
    """
    return __g.textEdits[i].toPlainText() if len(__g.textEdits) > i else None


def getCurrentTitle(i: int) -> str | None:
    """
    numにて指定するテキストボックスのタイトルを返す
    対応するラインエディットが存在しない場合Noneを返す
    """
    return __g.lineEdits[i].text() if len(__g.lineEdits) > i else None


def getAllCurrentText() -> list[str | None]:
    """
    すべてのテキストボックスのテキストをリストで返す
    """
    return [getCurrentText(i) for i in range(len(__g.textEdits))]


def getAllCurrentTitle() -> list[str | None]:
    """
    すべてのラインエディットのテキストをリストで返す
    """
    return [getCurrentTitle(i) for i in range(len(__g.lineEdits))]


def makeSaveData() -> dict:
    data: dict = {}
    texts = getAllCurrentText()
    titles = getAllCurrentTitle()
    for i, (text, title) in enumerate(zip(texts, titles)):
        data[i] = {}
        if type(text) is str:
            data[i]["text"] = text.rstrip("\r\n")
        data[i]["title"] = title
    settings = {
        key: value
        for key, value in __g.projectSettings.items()
        if key != "FileHistory"
    }
    return {"data": data, "settings": settings}


def makeDataToYaml(data: dict) -> str:
    try:
        return __y.safe_dump(data, allow_unicode=True)
    except (
        __y.YAMLError,
        __y.representer.RepresenterError,
        __y.resolver.ResolverError,
        __y.emitter.EmitterError,
    ) as e:
        __g.logger.error(f"Failed to dump Yaml data: {e}")
        return ""
        # ファイルが読み込めなかった場合


def saveProjectFile(filePath: str) -> bool:
    return FileOperation.writeToFile(makeDataToYaml(makeSaveData()), filePath)


def openProjectFile(filePath) -> dict:
    yml = FileOperation.openFile(filePath)
    dic: dict = {}
    if yml:
        try:
            dic = __y.safe_load(yml)
        except (
            KeyError,
            UnicodeDecodeError,
            __y.YAMLError,
            __y.scanner.ScannerError,
            __y.constructor.ConstructorError,
        ) as e:
            __g.logger.error(f"Failed to load Yaml data.: {e}")
    return dic


def setTextInTextBoxes(dic: dict):
    numberOfTextBoxes = len(__g.textEdits)
    for i in range(100):
        if i not in dic or i >= numberOfTextBoxes:
            pass
            return
        __g.textEdits[i].setPlainText(dic[i]["text"])
        __g.lineEdits[i].setText(dic[i]["title"])
        __g.textEditor.addReturn()
