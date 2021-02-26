from prediction.predictionTask import processTasks, PredictionTaskRet
from prediction.config import PREDICTION_TASK_TYPE_LBVS, PREDICTION_METRIC_TYPE_AUPR
from .forms import InfectiousDiseaseInputForm
from prediction.service import getCleanedSmilesInfoListFromInputForm
from typing import Sequence, List, Dict
from .modelConfig import MODEL_METRIC_PORT_DICT

__modelMetricPortDict = MODEL_METRIC_PORT_DICT


def doPrediction(modelTypes: Sequence, metric: str, smilesInfoList: List) \
        -> List[Dict[str, PredictionTaskRet]]:
    return processTasks(__modelMetricPortDict, modelTypes, metric, smilesInfoList, PREDICTION_TASK_TYPE_LBVS)


def processInfectiousDisease(request, inputForm: InfectiousDiseaseInputForm):
    smilesInfoList, invalidInputList = getCleanedSmilesInfoListFromInputForm(inputForm, request)
    if smilesInfoList:
        modelTypes = inputForm.cleaned_data['modelTypes']
        # inputMetric = inputForm.cleaned_data['metric']
        inputMetric = PREDICTION_METRIC_TYPE_AUPR
        preRetList, allSmilesDict = doPrediction(modelTypes, inputMetric, smilesInfoList)
    else:
        preRetList = None
    return preRetList, invalidInputList
