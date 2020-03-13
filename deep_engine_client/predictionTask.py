from deep_engine_client.dme.client import DMEClient
from typing import Sequence, List, Dict, Union

default_dme_server_host = "172.17.10.209"
default_dme_conn_timeout = 10

modelTypeAndPortDict = {
    "normal": 6000,
}


class PredictedRetUnit:
    def __init__(self, sampleId, err_code, result, smiles):
        self.sampleId = sampleId
        self.err_code = err_code
        self.result = result
        self.smiles = smiles

    def __iter__(self):
        return self


class PredictionTaskRet:
    def __init__(self, task_time, server_info, preResults: List[PredictedRetUnit]):
        self.taskTime = task_time
        self.serverInfo = server_info
        self.preResults = preResults


def predictSmiles(modelTypes: Sequence, smilesList, defaultRet=None) \
        -> Union[Dict[str, PredictionTaskRet], None]:
    if modelTypes is None or len(modelTypes) == 0:
        return defaultRet
    portModelTypeDict = {}
    for modelType in modelTypes:
        port = modelTypeAndPortDict.get(modelType, None)
        if port is not None:
            portModelTypeDict[port] = modelType
    if len(portModelTypeDict) > 0:
        # --- make client ---#
        client = DMEClient()
        ret = {}
        # define sample_id in order
        smilesDict = {}
        for i, smiles in enumerate(smilesList):
            smilesDict[i] = smiles

        # do tasks one by one
        for port, modelType in portModelTypeDict.items():
            worker = client.make_worker(default_dme_server_host, port, default_dme_conn_timeout)
            task_time, server_info, predicted_results = client.do_task(worker, smilesDict)
            modelRet = PredictionTaskRet(task_time, server_info,
                                         [PredictedRetUnit(record.sample_id, record.err_code, record.result,
                                                           smilesList[i])
                                          for i, record in enumerate(predicted_results)])
            ret[modelType] = modelRet
        return ret
    else:
        return defaultRet
