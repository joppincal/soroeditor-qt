import yaml

from soroeditor import __global__ as g
from soroeditor import FileOperation


def getCurrentText(i:int) -> str|None:
    '''
    numにて指定するテキストボックスのテキストを返す
    対応するテキストボックスが存在しない場合Noneを返す
    '''
    return g.textEdits[i].toPlainText() if len(g.textEdits) > i else None

def getAllCurrentText() -> list[str|None]:
    '''
    すべてのテキストボックスのテキストをリストで返す
    '''
    return [getCurrentText(i) for i in range(len(g.textEdits))]

def makeSaveData() -> dict:
    data = {}
    texts = getAllCurrentText()
    for i, text in enumerate(texts):
        data[i] = text.rstrip('\r\n')
    return data

def makeDataToYaml(data:dict) -> str:
    try:
        return yaml.safe_dump(data, allow_unicode=True)
    except (yaml.YAMLError, yaml.representer.RepresenterError, yaml.resolver.ResolverError, yaml.emitter.EmitterError) as e:
        g.logger.error(f'Failed to dump Yaml data: {e}')
        # ファイルが読み込めなかった場合

def saveProjectFile(filePath:str) -> bool:
    return FileOperation.writeToFile(makeDataToYaml(makeSaveData()), filePath)

def openProjectFile(filePath) -> (dict | None):
    yml = FileOperation.openFile(filePath)
    if yml:
        try:
            dic = yaml.safe_load(yml)
        except (KeyError, UnicodeDecodeError, yaml.YAMLError, yaml.scanner.ScannerError, yaml.constructor.ConstructorError) as e:
            g.logger.error(f'Failed to load yaml data.: {e}')
        return dic

def setTextInTextBoxes(dic:dict):
    numberOfTextBoxes = len(g.textEdits)
    for i in range(100):
        if i not in dic or i >= numberOfTextBoxes:
            pass
            return
        g.textEdits[i].setPlainText(dic[i])
        g.textEditor.addReturn()
