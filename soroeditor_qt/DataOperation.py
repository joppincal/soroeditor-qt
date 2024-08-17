import yaml as __y

from . import FileOperation, SettingOperation
from .logSetting import logSetting

logger = logSetting(__name__)


def makeSaveData(texts: list[str | None], titles: list[str | None]) -> dict:
    data: dict = {}
    for i, (text, title) in enumerate(zip(texts, titles)):
        data[i] = {}
        if type(text) is str:
            data[i]["text"] = text.rstrip("\r\n")
        data[i]["title"] = title
    settings = {
        key: value
        for key, value in SettingOperation.projectSettingData().items()
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
        logger.error(f"Failed to dump Yaml data: {e}")
        return ""
        # ファイルが読み込めなかった場合


def saveProjectFile(
    texts: list[str | None], titles: list[str | None], filePath: str
) -> bool:
    return FileOperation.writeToFile(
        makeDataToYaml(makeSaveData(texts, titles)), filePath
    )


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
            logger.error(f"Failed to load Yaml data.: {e}")
    return dic
