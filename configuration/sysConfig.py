import json
import os
import pandas as pd
import csv
from deep_engine_client.settings.settings import BASE_DIR, RUNTIME_ENV

CUSTOM_CONFIG_URL = os.path.join(BASE_DIR, 'configuration')

with open(os.path.join(CUSTOM_CONFIG_URL, f'{RUNTIME_ENV}_server_config.json'), 'r') as f:
    SYSTEM_CONFIG_DICT: dict = json.load(f)

PREDICTION_HOST = SYSTEM_CONFIG_DICT.get("predictionServerHost")
PREDICTION_CFG_PORT = SYSTEM_CONFIG_DICT.get("predictionServerCfgPort")


def generateModelPortCfgFile():
    categoryField = 'protein_class_name'
    modelNameField = 'uniprot_id'
    rawDF = pd.read_csv(os.path.join(BASE_DIR, "prediction/db/LBVS_size200_auroc50_reviewed.csv"))
    cfgDF = rawDF[[modelNameField, categoryField]].drop_duplicates()
    cfgDF['value'] = 1
    metricsDF = pd.DataFrame({"metrics": ['aupr'], "value": [1]})
    cfgDF = pd.merge(cfgDF, metricsDF, how='left', on='value')
    cfgDF.reset_index(inplace=True, drop=True)
    portDF = pd.DataFrame({"port": [str(i) for i in range(7300, 7300 + len(cfgDF.index), 1)]})
    cfgDF = cfgDF.join(portDF)
    cfgDF.reset_index(inplace=True, drop=True)
    cfgDF.to_csv(os.path.join(BASE_DIR, "configuration/targetFishing_model_port.csv"),
                 columns=[categoryField, 'metrics', modelNameField, 'port'], index=False, header=False)


def getModelPortCfg():
    with open(os.path.join(BASE_DIR, "configuration/targetFishing_model_port.csv"), 'r') as csvFile:
        csvReader = csv.reader(csvFile)
        modelCategoryDict = {}
        categoryModelDict = {}
        cateMetricModelPortDict = {}
        # init category dict
        # {
        #     category: {
        #         metrics:{
        #             model:port
        #         }
        #     }
        # }

        for row in csvReader:
            cate = row[0]
            metric = row[1]
            modelName = row[2]
            port = int(row[3])
            modelCategoryDict[modelName] = cate
            metricModelPortDict = cateMetricModelPortDict.get(cate, None)
            if metricModelPortDict is None:
                metricModelPortDict = {}
                cateMetricModelPortDict[cate] = metricModelPortDict
                categoryModelDict[cate] = []
            categoryModelDict[cate].append(modelName)
            modelPortDict = metricModelPortDict.get(metric)
            if modelPortDict is None:
                cateMetricModelPortDict[cate][metric] = {}
            cateMetricModelPortDict[cate][metric][modelName] = port

    return cateMetricModelPortDict, modelCategoryDict, categoryModelDict

    # def getModelPortCfg():


#     # get file from remote prediction-server by http
#     response = requests.get(f'http://{PREDICTION_HOST}:{PREDICTION_CFG_PORT}/targetFishing_model_port.csv')
#     if response.status_code == 200:
#         detectRet = chardet.detect(response.content)
#         content: str = response.content.decode(detectRet.get('encoding'))
#         lines = content.splitlines()
#         csvReader = csv.reader(lines)
#         # init category dict
#         modelPortDict = dict((cate, {}) for cate in PREDICTION_CATEGORY_NAME_DICT.keys())
#         modelCategoryDict = {}
#         categoryModelDict = dict((cate, []) for cate in PREDICTION_CATEGORY_NAME_DICT.keys())
#         for row in csvReader:
#             modelPortDict[row[0]][row[1]] = int(row[2])
#             categoryModelDict[row[0]].append(row[1])
#             modelCategoryDict[row[1]] = row[0]
#         return modelPortDict, modelCategoryDict, categoryModelDict
#     else:
#         raise CommonException("can not get model_port configuration!")


cmd = os.environ.get('RUNTIME_COMMAND')
if cmd and cmd == 'runserver':
    PREDICTION_CATE_METRIC_MODEL_PORT_DICT, PREDICTION_MODEL_CATEGORY_DICT, PREDICTION_CATEGORY_MODEL_DICT \
        = getModelPortCfg()
# AverageOperation_IN_RADAR_DICT = dict((cate, {}) for cate in PREDICTION_CATEGORY_NAME_DICT.keys())
# with open(os.path.join(CUSTOM_CONFIG_URL, 'average_operation_in_radar.csv'), 'r') as f:
#     for line in f.readlines():
#         rawData: list = line.strip().split(',')
#         category_model: list = rawData[0].split('_')
#         category = category_model[0]
#         model = category_model[1]
#         operation = int(rawData[1])
#         AverageOperation_IN_RADAR_DICT[category][model] = operation
# else:
#     PREDICTION_CATE_AND_MODEL_PORT_DICT, PREDICTION_MODEL_CATEGORY_DICT, PREDICTION_CATEGORY_MODEL_DICT = None, None, None
#     # AverageOperation_IN_RADAR_DICT = None
#
if __name__ == '__main__':
    generateModelPortCfgFile()
