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
METRIC_TYPE_AUPR = "aupr"
METRIC_TYPE_AUROC = "auroc"
DEFAULT_METRIC_TYPE = METRIC_TYPE_AUPR


# def generateModelPortCfgFile():
#     cfgDF = RAW_LBVS_PERFORMANCE_TABLE_DF[["modelName"]].drop_duplicates()
#     cfgDF['value'] = 1
#     metricsDF = pd.DataFrame({"metric": [DEFAULT_METRIC_TYPE], "value": [1]})
#     cfgDF = pd.merge(cfgDF, metricsDF, how='left', on='value')
#     cfgDF.reset_index(inplace=True, drop=True)
#     portDF = pd.DataFrame({"port": [str(i) for i in range(7300, 7300 + len(cfgDF.index), 1)]})
#     cfgDF = cfgDF.join(portDF)
#     cfgDF.reset_index(inplace=True, drop=True)
#     cfgDF.to_csv(os.path.join(BASE_DIR, "configuration/targetFishing_model_port.csv"),
#                  columns=['metric', "modelName", 'port'], index=False, header=False)


def getModelPortCfg():
    with open(os.path.join(BASE_DIR, "configuration/targetFishing_model_port.csv"), 'r') as csvFile:
        csvReader = csv.reader(csvFile)
        metricModelPortDict = {
            METRIC_TYPE_AUPR: {},
            METRIC_TYPE_AUROC: {}
        }
        # init category dict
        # {
    #         metrics:{
    #             model:port
    #         }
        # }

        for row in csvReader:
            metric = row[0]
            modelName = row[1]
            port = int(row[2])
            metricModelPortDict[metric][modelName] = port

    return metricModelPortDict


cmd = os.environ.get('RUNTIME_COMMAND')
if cmd and cmd == 'runserver':
    PREDICTION_METRIC_MODEL_PORT_DICT = getModelPortCfg()
else:
    PREDICTION_METRIC_MODEL_PORT_DICT = None
