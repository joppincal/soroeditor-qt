import yaml

from soroeditor import __global__ as g
from soroeditor import DataGet


def makeSaveData() -> dict:
    data = {}
    texts = DataGet.getAllCurrentText()
    for i, text in enumerate(texts):
        data[i] = text
    return data

def makeDataToYaml(data:dict) -> str:
    return yaml.safe_dump(data, allow_unicode=True)

def writeToFile(data:str, file_path:str):
    try:
        with open(file_path, mode='wt', encoding='utf-8') as f:
            # ファイルに書き込む
            f.write(data)
    except (FileNotFoundError, UnicodeDecodeError, yaml.YAMLError) as e:
        error_type = type(e).__name__
        error_message = str(e)
        g.logger.error(f"An error of type {error_type} occurred while writing to the file {file_path}: {error_message}")
    else:
        g.logger.info(f'Wrote to the file: {file_path}')
