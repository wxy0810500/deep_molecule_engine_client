import os
from deep_engine_client.settings.settings import BASE_DIR

MODEL_TYPE_STATMENT_DICT = {
    "TB18K_10uM": "Mtb model using 10uM as positive cutoff with 18886 training size",
    "TB13K_1uM": "Mtb model using 1uM as positive cutoff with 13000 training size",
    "Malaria16K_nochiral": "Malaria non-chiral model with 16k training size"
}

with open(os.path.join(os.path.join(BASE_DIR, 'infectiousDisease'), "model_metric_port.csv", 'r')) as f:
    MODEL_METRIC_PORT_DICT = {}
    for line in f.readlines():
        rawData: list = line.strip().split(',')
        model = rawData[0]
        metric = rawData[1]
        port = rawData[2]
        metricPortDict = MODEL_METRIC_PORT_DICT.get(model, None)
        if metricPortDict is None:
            metricPortDict = {}
            MODEL_METRIC_PORT_DICT[model] = metricPortDict
        metricPortDict[metric] = port
