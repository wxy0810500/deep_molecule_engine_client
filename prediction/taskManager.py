import os
from multiprocessing import Process, JoinableQueue as Queue, Manager
from typing import Dict
from .thrift.client import DMEClient


def _processWorker(processor, inputQueue: Queue, outputDict: Dict):
    client = DMEClient()
    while True:
        inputArg = inputQueue.get()
        if inputArg is None:
            continue
        #
        # print(inputArg)
        ret = processor(client, *inputArg['args'])
        outputDict[inputArg['taskId']] = ret


class PredictionTaskProcessPool:

    def __init__(self, processor):
        self._inputQueue = Queue()
        self._outputDict = Manager().dict()
        jobs = []
        for i in range(0, max(os.cpu_count() // 2, 4)):
            jobs.append(Process(target=_processWorker, args=(processor, self._inputQueue, self._outputDict)))
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

    def getTaskRet(self, taskId):
        return self._outputDict.get(taskId, None)


_g_Pool: PredictionTaskProcessPool = None


def initProcessPool(processor):
    global _g_Pool
    if _g_Pool is None:
        _g_Pool = PredictionTaskProcessPool(processor)
        _g_Pool.startAll()


def destroyProcessPool():
    global _g_Pool
    if _g_Pool is not None:
        _g_Pool.finishAll()


def getProcessPool():
    return _g_Pool
