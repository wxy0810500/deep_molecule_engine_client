from deep_engine_client.dme.client import DMEClient
from typing import Sequence, List, Dict, Union
from .sysConfig import SERVER_CONFIG_DICT

default_dme_server_host = SERVER_CONFIG_DICT.get("host")
default_dme_conn_timeout = SERVER_CONFIG_DICT.get("timeout")

modelTypeAndPortDict = SERVER_CONFIG_DICT.get("modelAndPort")


class PredictedRetUnit:

    def __init__(self, sampleId, label, modelType: int, ratings: str, smiles: str):
        self.sampleId = sampleId
        # results 格式 inactive-0-0.7889
        # errcode为0时：
        # "active" 是服务返回的标签；//用户关心
        # “1”     是模型返回的类别；
        # ”0.6089“是模型返回的预测打分 //用户关心
        self.label = label
        self.modelType = modelType
        self.ratings = ratings
        self.smiles = smiles

    @classmethod
    def commonOne(cls, sampleId, result: str, smiles: str):
        # results 格式 inactive-0-0.7889
        # errcode为0时：
        # "active" 是服务返回的标签；//用户关心
        # “1”     是模型返回的类别；
        # ”0.6089“是模型返回的预测打分 //用户关心
        retList = result.split('-')
        return cls(sampleId, retList[0], retList[1], retList[2], smiles)

    __invalid_unit_label: str = "invalid smiles string"
    __invalid_unit_ratings: str = ""

    @classmethod
    def invalidOne(cls, sampleId, smiles: str):
        return cls(sampleId, cls.__invalid_unit_label, 0, cls.__invalid_unit_ratings, smiles)

    __error_unit_label: str = "server_error"
    __error_unit_ratings: str = ""

    @classmethod
    def serverErrorOne(cls, sampleId, result: str):
        return cls(sampleId, cls.__error_unit_label, 0, cls.__error_unit_ratings, result)

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
            task_time, server_info, retUnitList, againDict = predictOnce(client, port, smilesDict)

            # again的 再处理一次 处理5次，若还不行，则放弃处理
            times = 1
            while len(againDict) > 0 and times <= 5:
                a_task_time, a_server_info, a_retUnitList, againDict = predictOnce(client, port, smilesDict)
                if len(a_retUnitList) > 0:
                    retUnitList.extend(a_retUnitList)
                times += 1

            modelRet = PredictionTaskRet(task_time, server_info, retUnitList)
            ret[modelType] = modelRet
        return ret
    else:
        return defaultRet


def predictOnce(client: DMEClient, port: int, smilesDict: dict):
    worker = client.make_worker(default_dme_server_host, port, default_dme_conn_timeout)
    task_time, server_info, predicted_results = client.do_task(worker, smilesDict)
    retUnitList = []
    againDict = {}
    # 根据err_code分别处理
    for i, record in enumerate(predicted_results):
        if record.err_code == 0:
            retUnitList.append(PredictedRetUnit.commonOne(record.sample_id, record.result, smilesDict[i]))
        elif record.err_code == 1:
            againDict[i] = smilesDict[i]
        elif record.err_code == 2:
            retUnitList.append(PredictedRetUnit.invalidOne(record.sample_id, smilesDict[i]))
        else:
            retUnitList.append(PredictedRetUnit.serverErrorOne(record.sample_id, record.result))

    return task_time, server_info, retUnitList, againDict
