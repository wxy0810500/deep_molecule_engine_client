from prediction.thrift.client import DMEClient
import uuid
from typing import Sequence, List, Dict
from utils.timeUtils import sleepWithSwitchInterval
from utils.debug import printDebug
from deep_engine_client.exception import PredictionCommonException
from .taskManager import getProcessPool
from .config import *

__default_dme_server_host = PREDICTION_SERVER_HOST
__default_dme_conn_timeout = PREDICTION_SERVER_TIMEOUT


class PredictedRetUnit:

    def __init__(self, sampleId, label, classIdx, score: float, smilesInfoDict: Dict):
        self.sampleId = sampleId
        # results 格式 inactive-0-0.7889
        # errcode为0时：
        # "active" 是服务返回的标签；//用户关心
        # “1”     是模型返回的类别；classIdx //排序依据
        # ”0.6089“是模型返回的预测打分 //用户关心
        self.label = label
        self.classIdx = 0 if (classIdx is None or classIdx == 'None') else int(classIdx)
        self.score = score if self.classIdx != 0 else 1.0 - score
        self.input = smilesInfoDict['input']
        self.drugName = smilesInfoDict['drug_name']
        self.cleanedSmiles = smilesInfoDict['cleaned_smiles']

    @classmethod
    def commonOne(cls, sampleId, result: str, smilesInfoDict: Dict):
        # results 格式 inactive-0-0.7889
        # errcode为0时：
        # "active" 是服务返回的标签；//用户关心
        # “1”     是模型返回的类别；
        # ”0.6089“是模型返回的预测打分 //用户关心
        label, classIdx, score = result.split('-')
        return cls(sampleId, label, classIdx, float(score), smilesInfoDict)

    __error_unit_score: float = -1.0
    queue_full_unit_label: str = "input queue is full, try later"
    invalid_smiles_unit_label: str = "invalid smiles string"
    task_timeout_unit_label: str = "time out for task"
    server_error_unit_label: str = "Unknown exception encountered, please report to us"

    @classmethod
    def errorOne(cls, sampleId, label: str, smilesInfoDict):
        return cls(sampleId, label, None, cls.__error_unit_score, smilesInfoDict)

    def __iter__(self):
        return self


class PredictionTaskRet:
    def __init__(self, task_time, server_info, preResults: List[PredictedRetUnit]):
        self.taskTime = task_time
        self.serverInfo = server_info
        self.preResults = preResults


def processTasks(modelTypeAndPortDict: Dict, modelTypes: Sequence, metric: str,
                 smilesInfoList, taskType, aux_data=None) \
        -> Dict[str, PredictionTaskRet]:
    """


    @param metric:
    @param modelTypes:
    @param modelTypeAndPortDict:
    @param smilesInfoList:
    @param taskType:
    @param aux_data:
    @return:
            {
                modelName:PredictionTaskRet
            }
    """
    if modelTypes is None or len(modelTypes) == 0:
        raise PredictionCommonException('We will support these model types as soon as possible!')
    modelPortDict = {}
    for modelType in modelTypes:
        metricAndPort = modelTypeAndPortDict.get(modelType, None)
        if metricAndPort is not None:
            port = metricAndPort.get(metric, None)
            if port is not None:
                modelPortDict[modelType] = port
    if len(modelPortDict) <= 0:
        raise PredictionCommonException('We will support these model types as soon as possible!')
    # --- make client ---#
    retList = []
    # define smiles_index in order
    smilesDictList = []
    allSmilesDict = {}
    for i, smilesInfo in enumerate(smilesInfoList):
        if i % 50 == 0:
            smilesDict = {}
            smilesDictList.append(smilesDict)
        smilesDict[i] = smilesInfo
        allSmilesDict[i] = smilesInfo
    for smilesDict in smilesDictList:
        # do tasks one by one
        processPool = getProcessPool()
        taskInfoDict: dict = {}
        for modelName, port in modelPortDict.items():
            taskId = uuid.uuid1()
            taskInfoDict[taskId] = modelName
            taskArgs = {
                "taskId": taskId,
                "args": (__default_dme_server_host, port, __default_dme_conn_timeout, taskType, smilesDict, aux_data),
                "errorCode": "failed"
            }
            processPool.putTask(taskArgs)
        retDict = {}
        while True:
            sleepWithSwitchInterval(10)
            finishedTaskIds = []
            for taskId, modelName in taskInfoDict.items():
                taskRet = processPool.getTaskRet(taskId)
                if taskRet:
                    if type(taskRet) == PredictionTaskRet:
                        retDict[modelName] = taskRet
                    else:
                        printDebug(taskRet.get("errorMessage", None))
                    finishedTaskIds.append(taskId)
            if len(finishedTaskIds) > 0:
                for taskId in finishedTaskIds:
                    taskInfoDict.pop(taskId)
                finishedTaskIds.clear()
            if len(taskInfoDict) == 0:
                break
        retList.append(retDict)
    return retList, allSmilesDict


def processOneTask(client: DMEClient, *args):
    """

    @param client:
    @param args:
    @return: PredictionTaskRet
    """
    # print(args)
    host = args[0]
    port: int = args[1]
    timeout = args[2]
    taskType = args[3]
    smilesDict: dict = args[4]
    aux_data = args[5]
    client_worker = client.make_worker(host, port, timeout)
    task_time, server_info, retUnitList, againDict = _predictOnce(client, client_worker, taskType, smilesDict, aux_data)

    # again的 再处理一次 处理5次，若还不行，则放弃处理
    times = 1
    while len(againDict) > 0 and times <= 5:
        a_task_time, a_server_info, a_retUnitList, againDict = \
            _predictOnce(client, client_worker, taskType, smilesDict, aux_data)
        if len(a_retUnitList) > 0:
            retUnitList.extend(a_retUnitList)
        times += 1
    if len(againDict) > 0:
        # 多次处理依然不行，则放弃处理，
        for sampleId, smilesInfo in againDict.items():
            retUnitList.append(PredictedRetUnit.errorOne(sampleId,
                                                         PredictedRetUnit.queue_full_unit_label, smilesInfo))
    # # sort result
    retUnitList = sorted(retUnitList, key=lambda unit: unit.score, reverse=True)
    modelRet = PredictionTaskRet(task_time, server_info, retUnitList)
    return modelRet


def _predictOnce(client: DMEClient, client_worker, task, smilesDict: dict, aux_data):
    task_time, server_info, predicted_results = client.do_task(client_worker, task, smilesDict, aux_data)
    # print(predicted_results)
    retUnitList = []
    againDict = {}
    # 根据err_code分别处理
    for record in predicted_results:
        smilesIndex = int(record.sample_id)
        smiles = smilesDict[smilesIndex]
        if record.err_code == 0:
            retUnitList.append(PredictedRetUnit.commonOne(record.sample_id, record.result, smiles))
            # 根据RetUnit中的classIdx排序
        elif record.err_code == 1:
            # input queue full, do infectiousDisease again
            againDict[smilesIndex] = smiles
        elif record.err_code == 2:
            # invalid smiles
            retUnitList.append(PredictedRetUnit.errorOne(record.sample_id,
                                                         PredictedRetUnit.invalid_smiles_unit_label, smiles))
        elif record.err_code == 3:
            # time out for task
            retUnitList.append(PredictedRetUnit.errorOne(record.sample_id,
                                                         PredictedRetUnit.task_timeout_unit_label, smiles))
        else:
            retUnitList.append(PredictedRetUnit.errorOne(record.sample_id,
                                                         PredictedRetUnit.server_error_unit_label, smiles))

    return task_time, server_info, retUnitList, againDict