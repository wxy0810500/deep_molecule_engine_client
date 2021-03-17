import os
from deep_engine_client.settings.settings import BASE_DIR

MODEL_TYPE_STATEMENT_DICT = {
    "TB18K_10uM": "TB13K: Mtb model using 10uM as positive cutoff with 18886 training size",
    "TB13K": "TB13K: Mtb model using 1uM as positive cutoff with 13475 training size",
    "Malaria_16K_non-chiral": "Malaria 16K non-chiral: Malaria non-chiral model with 16932 training size",
    "Malaria_93K_chiral": "Malaria 93K chiral: Malaria chiral model with 93156 training size"
}


with open(os.path.join(os.path.join(BASE_DIR, 'infectiousDisease'), "model_metric_port.csv"), 'r') as f:
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
        metricPortDict[metric] = int(port)