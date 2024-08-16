import copy

import yaml as __y
from PySide6.QtGui import QFontDatabase

from . import DataOperation as __d
from . import FileOperation as __f
from .logSetting import logSetting

logger = logSetting(__name__)

__PATH = "./setting.yaml"

__DEFAULTSETTINGDATA = {
    "FileHistory": [],
    "Font": "",
    "FontSize": 0,
    "FontStyle": "",
    "Resizable": False,
    "Size": [800, 600],
    "ToolBar": {
        1: {
            "Area": "Top",
            "Contents": [
                "NewFile",
                "OpenFile",
                "SaveFile",
                "SaveFileAs",
                "Setting",
            ],
            "Enable": True,
            "Title": "ツールバー1",
        },
        2: {
            "Area": "Bottom",
            "Contents": [
                "CurrentPlace",
                "Info",
            ],
            "Enable": True,
            "Title": "ツールバー2",
        },
    },
    "Version": "0.0.0",
}

__globalSettingData: dict

__projectSettingData: dict


def openSettingFile() -> dict:
    dic: dict = {}
    yml = __f.openFile(__PATH)
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


def writeSettingFile(data: dict) -> bool:
    return __f.writeToFile(__d.makeDataToYaml(data), __PATH)


def makeNewSettingFile() -> bool:
    return writeSettingFile(__DEFAULTSETTINGDATA)


def settingVerification(dic: dict) -> dict:
    size = dic.get("Size", None)
    resizable = dic.get("Resizable", None)
    font = dic.get("Font", None)
    fontStyle = dic.get("FontStyle", None)
    fontSize = dic.get("FontSize", None)
    fileHistory = dic.get("FileHistory", None)
    toolBar = dic.get("ToolBar", None)

    default = defaultSettingData()

    if (
        type(size) is list
        and len(size) == 2
        and all([type(i) is int for i in size])
    ):
        pass
    elif size in ("Maximize", "FullScreen"):
        pass
    else:
        dic["Size"] = default["Size"]

    if isinstance(resizable, bool):
        pass
    else:
        dic["Resizable"] = default["Resizable"]

    if font in QFontDatabase.families(QFontDatabase.WritingSystem.Any):
        pass
    else:
        dic["Font"] = default["Font"]

    if fontStyle in QFontDatabase.styles(font):
        pass
    else:
        dic["FontStyle"] = default["FontStyle"]

    if type(fontSize) is int and fontSize >= 0:
        pass
    else:
        dic["FontSize"] = default["FontSize"]

    if type(fileHistory) is list:
        pass
    else:
        dic["FileHistory"] = default["FileHistory"]

    if type(toolBar) is dict:
        pass
    else:
        dic["ToolBar"] = default["ToolBar"]

    return dic


def defaultSettingData() -> dict:
    return copy.deepcopy(__DEFAULTSETTINGDATA)


def globalSettingData() -> dict:
    return copy.deepcopy(__globalSettingData)


def setGlobalSettingData(dic: dict):
    dic = settingVerification(dic)
    global __globalSettingData
    __globalSettingData = dic


def projectSettingData() -> dict:
    return copy.deepcopy(__projectSettingData)


def setProjectSettingData(dic: dict):
    dic = settingVerification(dic)
    global __projectSettingData
    __projectSettingData = dic
