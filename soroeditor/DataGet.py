from soroeditor import __global__ as g


def getCurrentText(i:int) -> str|None:
    '''
    numにて指定するテキストボックスのテキストを返す
    対応するテキストボックスが存在しない場合Noneを返す
    '''
    return g.textBoxes[i].toPlainText() if len(g.textBoxes) > i else None

def getAllCurrentText() -> list[str|None]:
    '''
    すべてのテキストボックスのテキストをリストで返す
    '''
    return [getCurrentText(i) for i in range(len(g.textBoxes))]
