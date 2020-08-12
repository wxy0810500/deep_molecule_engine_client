import os
from multiprocessing import Process, JoinableQueue as Queue
from typing import Sequence, Dict

from deep_engine_client.exception import PredictionCommonException
from deep_engine_client.sysConfig import SERVER_CONFIG_DICT
from .predictionTask import PredictionTaskRet, doPredictionOnce, PredictedRetUnit
from .thrift.client import DMEClient

efault_dme_server_host = SERVER_CONFIG_DICT.get("host")
default_dme_conn_timeout = SERVER_CONFIG_DICT.get("timeout")

LigandModelTypeAndPortDict = SERVER_CONFIG_DICT.get("modelAndPort").get('ligand')
StructureModelTypeAndPortDict = SERVER_CONFIG_DICT.get("modelAndPort").get('structure')

PREDICTION_TASK_TYPE_LIGAND = "LBVS"
PREDICTION_TASK_TYPE_STRUCTURE = "SBVS"


class PredictionTaskProcessPool:

    def __init__(self):
        self._inputQueue = Queue()
        self._outputQueue = Queue()
        jobs = []
        for i in range(0, os.cpu_count()):
            jobs.append(Process(target=_processWorker, args=(self._inputQueue, self._outputQueue)))
        self._jobs = jobs

    def startAll(self):
        for p in self._jobs:
            p.start()

    def finishAll(self):
        for p in self._jobs:
            p.terminate()
            p.close()

    def putTask(self, taskArgs, block=True, timeout=None):
        self._inputQueue.put(taskArgs, block=block, timeout=timeout)

    def getTaskRet(self, block=True, timeout=None):
        return self._outputQueue.get(block=block, timeout=timeout)


def _processWorker(inputQueue: Queue, outputQueue: Queue):
    client = DMEClient()
    while True:
        inputArg = inputQueue.get()
        if inputArg is None:
            continue
        ret = doPredictionOnce(inputArg, client)
        outputQueue.put(ret)


def processTasks(modelTypeAndPortDict: Dict, modelTypes: Sequence, smilesInfoList, taskType, aux_data=None) \
        -> Dict[str, PredictionTaskRet]:
    """


    @param modelTypeAndPortDict:
    @param modelTypes:
    @param smilesInfoList:
    @param taskType:
    @param aux_data:
    @return:
    """
    if modelTypes is None or len(modelTypes) == 0:
        raise PredictionCommonException('We will support these model types as soon as possible!')
    portModelTypeDict = {}
    for modelType in modelTypes:
        data = modelTypeAndPortDict.get(modelType, None)
        if data is not None and data[1] != 0:
            portModelTypeDict[data[1]] = data[0]
    if len(portModelTypeDict) > 0:
        # --- make client ---#
        client = DMEClient()
        ret = {}
        # define sample_id in order
        smilesDict = {}
        for i, smilesInfo in enumerate(smilesInfoList):
            smilesDict[i] = smilesInfo

        # do tasks one by one
        for port, modelName in portModelTypeDict.items():
            ret[modelName] = modelRet
        return ret
    else:
        raise PredictionCommonException('We will support these model types as soon as possible!')


def _processOneTask(client: DMEClient, port: int, taskType, smilesDict: dict, aux_data):
    task_time, server_info, retUnitList, againDict = _predictOnce(client_worker, port, taskType, smilesDict, aux_data)

    # again的 再处理一次 处理5次，若还不行，则放弃处理
    times = 1
    while len(againDict) > 0 and times <= 5:
        a_task_time, a_server_info, a_retUnitList, againDict = \
            _predictOnce(client, port, taskType, smilesDict, aux_data)
        if len(a_retUnitList) > 0:
            retUnitList.extend(a_retUnitList)
        times += 1
    if len(againDict) > 0:
        # 多次处理依然不行，则放弃处理，
        for sampleId, smilesInfo in againDict.items():
            retUnitList.append(PredictedRetUnit.errorOne(sampleId,
                                                         PredictedRetUnit.queue_full_unit_label, smilesInfo))
    # sort result
    retUnitList = sorted(retUnitList, key=lambda unit: unit.score, reverse=True)
    modelRet = PredictionTaskRet(task_time, server_info, retUnitList)


def _predictOnce(client: DMEClient, port: int, task, smilesDict: dict, aux_data):
    worker = client.make_worker(default_dme_server_host, port, default_dme_conn_timeout)
    task_time, server_info, predicted_results = client.do_task(worker, task, smilesDict, aux_data)
    # print(predicted_results)
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
