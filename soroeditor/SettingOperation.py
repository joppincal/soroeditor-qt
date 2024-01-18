import copy

import yaml as __y

from soroeditor import DataOperation as __d
from soroeditor import FileOperation as __f
from soroeditor import __global__ as __g

__PATH = "./setting.yaml"

__DEFAULTSETTINGDATA = {
    "FileHistory": [],
    "Font": "MS UI Gothic",
    "FontSize": 11,
    "Size": (800, 600),
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
}


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
            __g.logger.error(f"Failed to load Yaml data.: {e}")
    return dic


def writeSettingFile(data: dict) -> bool:
    return __f.writeToFile(__d.makeDataToYaml(data), __PATH)


def makeNewSettingFile() -> bool:
    return writeSettingFile(__DEFAULTSETTINGDATA)


def ValidateContentsOfSettingFile(dic: dict) -> bool:
    return set(dic.keys()) <= {
        "FileHistory",
        "Font",
        "FontSize",
        "Size",
        "ToolBar",
    }


def defaultSettingData() -> dict:
    return copy.deepcopy(__DEFAULTSETTINGDATA)
