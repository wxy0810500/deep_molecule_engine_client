import json
import os
import requests
import csv
import chardet
from deep_engine_client.exception import CommonException

from deep_engine_client.settings.settings import BASE_DIR, RUNTIME_ENV

CUSTOM_CONFIG_URL = os.path.join(BASE_DIR, 'configuration')

with open(os.path.join(CUSTOM_CONFIG_URL, f'{RUNTIME_ENV}_server_config.json'), 'r') as f:
    SYSTEM_CONFIG_DICT: dict = json.load(f)

PREDICTION_HOST = SYSTEM_CONFIG_DICT.get("predictionServerHost")
PREDICTION_CFG_PORT = SYSTEM_CONFIG_DICT.get("predictionServerCfgPort")
PREDICTION_CATEGORY_NAME_DICT = {
                                    "A": "Absorption",
                                    "D": "Distribution",
                                    "M": "Metabolism",
                                    "E": "Excretion",
                                    "T": "Toxicity",
                                    "P": "Mechanism Protein"
                                }
PREDICTION_CATEGORYS_IN_RADAR = ["A", "D", "M", "E", "T"]
PREDICTION_METRICS_NAME_DICT = {"aupr": "AuPR",
                                "auc": "AuROC",
                                }
                                # "p": "Precision",
                                # "r": 'Recall'}


def getModelPortCfg():
    # get file from remote prediction-server by http
    response = requests.get(f'http://{PREDICTION_HOST}:{PREDICTION_CFG_PORT}/admet_model_port.csv')

    if response.status_code == 200:
        detectRet = chardet.detect(response.content)
        content: str = response.content.decode(detectRet.get('encoding'))
        lines = content.splitlines()
        # category, metrics, modelType, port
        csvReader = csv.reader(lines)
        # init category dict
        # {
        #     category: {
        #         metrics:{
        #             model:port
        #         }
        #     }
        # }
        modelPortDict = dict((cate, dict((metrics, {}) for metrics in PREDICTION_METRICS_NAME_DICT.keys()))
                             for cate in PREDICTION_CATEGORY_NAME_DICT.keys())
        modelCategoryDict = {}
        categoryModelDict = dict((cate, []) for cate in PREDICTION_CATEGORY_NAME_DICT.keys())
        # row: category, metrics, modelType, port
        for row in csvReader:
            modelPortDict[row[0]][row[1]][row[2]] = int(row[3])
            categoryModelDict[row[0]].append(row[2])
            modelCategoryDict[row[2]] = row[0]
        return modelPortDict, modelCategoryDict, categoryModelDict
    else:
        raise CommonException("can not get model_port configuration!")


cmd = os.environ.get('RUNTIME_COMMAND')
if cmd and cmd == 'runserver':
    PREDICTION_MODEL_PORT_DICT, PREDICTION_MODEL_CATEGORY_DICT, PREDICTION_CATEGORY_MODEL_DICT = getModelPortCfg()
    AverageOperation_IN_RADAR_DICT = dict((cate, {}) for cate in PREDICTION_CATEGORYS_IN_RADAR)
    with open(os.path.join(CUSTOM_CONFIG_URL, 'average_operation_in_radar.csv'), 'r') as f:
        for line in f.readlines():
            rawData: list = line.strip().split(',')
            category_model: list = rawData[0].split('_')
            category = category_model[0]
            model = category_model[1]
            operation = int(rawData[1])
            AverageOperation_IN_RADAR_DICT[category][model] = operation
else:
    PREDICTION_MODEL_PORT_DICT, PREDICTION_MODEL_CATEGORY_DICT, PREDICTION_CATEGORY_MODEL_DICT = None, None, None
    AverageOperation_IN_RADAR_DICT = None
#
# if __name__ == '__main__':
#     print(PREDICTION_MODEL_PORT_DICT, PREDICTION_MODEL_CATEGORY_DICT)
