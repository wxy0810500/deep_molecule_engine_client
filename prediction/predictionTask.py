from .thrift.client import DMEClient
from typing import Sequence, List, Dict
from deep_engine_client.sysConfig import SERVER_CONFIG_DICT
from time import sleep
from deep_engine_client.exception import PredictionCommonException

default_dme_server_host = SERVER_CONFIG_DICT.get("host")
default_dme_conn_timeout = SERVER_CONFIG_DICT.get("timeout")

LigandModelTypeAndPortDict = SERVER_CONFIG_DICT.get("modelAndPort").get('ligand')
StructureModelTypeAndPortDict = SERVER_CONFIG_DICT.get("modelAndPort").get('structure')

PREDICTION_TASK_TYPE_LIGAND = "LBVS"
PREDICTION_TASK_TYPE_STRUCTURE = "SBVS"


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


def predictLigand(modelTypes: Sequence, smilesInfoList: List) -> Dict[str, PredictionTaskRet]:
    return _doPredict(LigandModelTypeAndPortDict, modelTypes, smilesInfoList, PREDICTION_TASK_TYPE_LIGAND)


def predictStructure(modelTypes: Sequence, smilesInfoList: List, pdbContent) -> Dict[str, PredictionTaskRet]:
    return _doPredict(StructureModelTypeAndPortDict, modelTypes, smilesInfoList, PREDICTION_TASK_TYPE_STRUCTURE,
                      pdbContent)


def _doPredict(modelTypeAndPortDict: Dict, modelTypes: Sequence, smilesInfoList, task, aux_data=None) \
        -> Dict[str, PredictionTaskRet]:
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
            task_time, server_info, retUnitList, againDict = _predictOnce(client, port, task, smilesDict, aux_data)

            # again的 再处理一次 处理5次，若还不行，则放弃处理
            times = 1
            while len(againDict) > 0 and times <= 5:
                sleep(1)
                a_task_time, a_server_info, a_retUnitList, againDict = \
                    _predictOnce(client, port, task, smilesDict, aux_data)
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
            ret[modelName] = modelRet
        return ret
    else:
        raise PredictionCommonException('We will support these model types as soon as possible!')


def _predictOnce(client: DMEClient, port: int, task, smilesDict: dict, aux_data):
    worker = client.make_worker(default_dme_server_host, port, default_dme_conn_timeout)
    task_time, server_info, predicted_results = client.do_task(worker, task, smilesDict, aux_data)
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
