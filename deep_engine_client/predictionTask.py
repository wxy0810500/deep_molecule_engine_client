from deep_engine_client.dme.client import DMEClient
from typing import Sequence, List, Dict, Union
from .sysConfig import SERVER_CONFIG_DICT
from time import sleep

default_dme_server_host = SERVER_CONFIG_DICT.get("host")
default_dme_conn_timeout = SERVER_CONFIG_DICT.get("timeout")

modelTypeAndPortDict = SERVER_CONFIG_DICT.get("modelAndPort")


class PredictedRetUnit:

    def __init__(self, sampleId, label, classIdx: int, score: str, smiles: str):
        self.sampleId = sampleId
        # results 格式 inactive-0-0.7889
        # errcode为0时：
        # "active" 是服务返回的标签；//用户关心
        # “1”     是模型返回的类别；classIdx //排序依据
        # ”0.6089“是模型返回的预测打分 //用户关心
        self.label = label
        self.classIdx = classIdx
        self.score = score
        self.smiles = smiles

    @classmethod
    def commonOne(cls, sampleId, result: str, smiles: str):
        # results 格式 inactive-0-0.7889
        # errcode为0时：
        # "active" 是服务返回的标签；//用户关心
        # “1”     是模型返回的类别；
        # ”0.6089“是模型返回的预测打分 //用户关心
        label, classIdx, score = result.split('-')
        return cls(sampleId, label, int(classIdx), float(score), smiles)

    __error_unit_score: float = -1.0
    queue_full_unit_label: str = "input queue is full, try later"
    invalid_smiles_unit_label: str = "invalid smiles string"
    task_timeout_unit_label: str = "time out for task"
    server_error_unit_label: str = "Unknown exception encountered, please report to us"

    @classmethod
    def errorOne(cls, sampleId, label: str, smiles: str):
        return cls(sampleId, label, None, cls.__error_unit_score, smiles)

    def __iter__(self):
        return self


class PredictionTaskRet:
    def __init__(self, task_time, server_info, preResults: List[PredictedRetUnit]):
        self.taskTime = task_time
        self.serverInfo = server_info
        self.preResults = preResults


def sortPredictedRetUnitListByActiveScore(unitList: List[PredictedRetUnit]):
    for unit in unitList:
        if unit.classIdx == 0:
            unit.score = 1.0 - unit.score
    return sorted(unitList, key=lambda x: x.score, reverse=True)


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
                sleep(2)
                a_task_time, a_server_info, a_retUnitList, againDict = predictOnce(client, port, smilesDict)
                if len(a_retUnitList) > 0:
                    retUnitList.extend(a_retUnitList)
                times += 1
            if len(againDict) > 0:
                # 多次处理依然不行，则放弃处理，
                for sampleId, smiles in againDict.items():
                    retUnitList.append(PredictedRetUnit.errorOne(sampleId,
                                                                 PredictedRetUnit.queue_full_unit_label, smiles))
            # sort_by_active_score
            modelRet = PredictionTaskRet(task_time, server_info, sortPredictedRetUnitListByActiveScore(retUnitList))
            ret[modelType] = modelRet
        return ret
    else:
        return defaultRet


def predictOnce(client: DMEClient, port: int, smilesDict: dict):
    worker = client.make_worker(default_dme_server_host, port, default_dme_conn_timeout)
    task_time, server_info, predicted_results = client.do_task(worker, smilesDict)
    print(predicted_results)
    retUnitList = []
    againDict = {}
    # 根据err_code分别处理
    for i, record in enumerate(predicted_results):
        if record.err_code == 0:
            retUnitList.append(PredictedRetUnit.commonOne(record.sample_id, record.result, smilesDict[i]))
            # 根据RetUnit中的classIdx排序
        elif record.err_code == 1:
            # input queue full, dict again
            againDict[i] = smilesDict[i]
        elif record.err_code == 2:
            # invalid smiles
            retUnitList.append(PredictedRetUnit.errorOne(record.sample_id,
                                                         PredictedRetUnit.invalid_smiles_unit_label, smilesDict[i]))
        elif record.err_code == 3:
            # time out for task
            retUnitList.append(PredictedRetUnit.errorOne(record.sample_id,
                                                         PredictedRetUnit.task_timeout_unit_label, smilesDict[i]))
        else:
            retUnitList.append(PredictedRetUnit.errorOne(record.sample_id,
                                                         PredictedRetUnit.server_error_unit_label, smilesDict[i]))

    return task_time, server_info, retUnitList, againDict
