from soroeditor import __global__ as g


class DataGetClass:
    def getCurrentText(self, i:int):
        '''
        numにて指定するテキストボックスのテキストを返す
        対応するテキストボックスが存在しない場合Noneを返す
        '''
        return g.textBoxes[i].toPlainText() if len(g.textBoxes) > i else None

    def getAllCurrentText(self):
        '''
        すべてのテキストボックスのテキストをリストで返す
        '''
        return [self.getCurrentText(i) for i in range(len(g.textBoxes))]
