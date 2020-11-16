import json
import os

from deep_engine_client.settings.settings import BASE_DIR, RUNTIME_ENV

CUSTOM_CONFIG_URL = os.path.join(BASE_DIR, 'configuration')

with open(os.path.join(CUSTOM_CONFIG_URL, f'{RUNTIME_ENV}_server_config.json'), 'r') as f:
    SYSTEM_CONFIG_DICT: dict = json.load(f)

# def getModelPortCfg():
#     # get file from remote prediction-server by http
#     response = requests.get(f'http://{PREDICTION_HOST}:5555/admet_model_port.csv')
#     if response.status_code == 200:
#         detectRet = chardet.detect(response.content)
#         content: str = response.content.decode(detectRet.get('encoding'))
#         lines = content.splitlines()
#         csvReader = csv.reader(lines)
#         # init category dict
#         modelPortDict = dict((category, {}) for category in PREDICTION_CATEGORY_NAME_DICT.keys())
#         modelCategoryDict = {}
#         categoryModelDict = dict((category, []) for category in PREDICTION_CATEGORY_NAME_DICT.keys())
#         for row in csvReader:
#             modelPortDict[row[0]][row[1]] = int(row[2])
#             categoryModelDict[row[0]].append(row[1])
#             modelCategoryDict[row[1]] = row[0]
#         return modelPortDict, modelCategoryDict, categoryModelDict
#     else:
#         raise CommonException("can not get model_port configuration!")

#
#
# , PREDICTION_MODEL_CATEGORY_DICT, PREDICTION_CATEGORY_MODEL_DICT = getModelPortCfg()

