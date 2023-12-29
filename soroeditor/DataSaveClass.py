import yaml

from soroeditor import __global__ as g
from soroeditor.DataGetClass import DataGetClass


class DataSaveClass:
    def makeSaveData(self) -> dict:
        data = {}
        texts = DataGetClass().getAllCurrentText()
        return data

    def makeDataToYaml(self, data:dict):
        return yaml.safe_dump(data, encoding='utf-8', allow_unicode=True)

    def writeToFile(self, data:dict, file_path:str):
        try:
            with open(file_path, mode='wt', encoding='utf-8') as f:
                # ファイルに書き込む
                yaml.safe_dump(data, f, encoding='utf-8', allow_unicode=True)
                # 変更前のデータを更新する（変更検知に用いられる）
                self.data = data
        except (FileNotFoundError, UnicodeDecodeError, yaml.YAMLError) as e:
            error_type = type(e).__name__
            error_message = str(e)
            g.logger.error(f"An error of type {error_type} occurred while writing to the file {file_path}: {error_message}")
        else:
            g.logger.info(f'Wrote to the file: {file_path}')
