# -*- coding: utf-8 -*-

from typing import Dict, List

from django.http import HttpResponseBadRequest
from django.shortcuts import reverse
from django_excel import make_response
from pyexcel import Book

from configuration.sysConfig import PREDICTION_MODEL_CATEGORY_DICT
from deep_engine_client.exception import *
from deep_engine_client.tables import InvalidInputsTable
from .forms import *
from .predictionTask import PredictionTaskRet, PREDICTION_TYPE_ADMET
from configuration.sysConfig import PREDICTION_CATEGORY_NAME_DICT
from .service import processADMET
from .tables import *

INPUT_TEMPLATE_FORMS = {
    PREDICTION_TYPE_ADMET: {
        'inputForm': ADMETModelInputForm(),
        "pageTitle": "admet",
    }
}


def _formatRetExcelBook(preRet: Dict[str, PredictionTaskRet], invalidInputList):
    sheets = {}
    headers = ['', 'Score', 'Input{name|smiles}', 'DrugName', 'CleanedSmiles']
    if preRet:
        for modelType, preRetRecord in preRet.items():
            records = [[sid + 1,  # id
                        '%0.4f' % preRetUnit.score if preRetUnit.score >= 0 else None,  # score
                        preRetUnit.input,  # input
                        preRetUnit.drugName,  # "drugName":
                        preRetUnit.cleanedSmiles]  # "cleanedSmiles":
                       for sid, preRetUnit in enumerate(preRetRecord.preResults)]
            rows = [['time = %0.2fs' % preRetRecord.taskTime], headers] + records
            sheets[modelType] = rows
    if invalidInputList and len(invalidInputList) > 0:
        sheets['invalidInputs'] = [[invalidInput] for invalidInput in invalidInputList]
    return Book(sheets)


def _formatRetTables(preRet: Dict[str, PredictionTaskRet], inputCategorys: List[str], smilesDict: Dict[str, str]):
    # tables for each smiles
    # {
    #     smilesIndex: {
    #         category1:[
    #             {
    #                 "modelName":modelName,
    #                 "score": score
    #             },
    #             {
    #                 "modelName": modelName,
    #                 "score": score
    #             }
    #         ],
    #         category2: [
    #             {
    #                 "modelName":modelName,
    #                 "score": score
    #             }
    #         ]
    #     }
    # }
    retDict = dict((smilesIndex, dict((category, []) for category in inputCategorys))
                   for smilesIndex in smilesDict.keys())
    for modelType, preRetRecord in preRet.items():
        category = PREDICTION_MODEL_CATEGORY_DICT.get(modelType, None)
        if category is None:
            category = "unsupported"
        for retUnit in preRetRecord.preResults:
            smilesIndex: int = int(retUnit.sampleId)
            retDict[smilesIndex][category].append({
                "model": modelType,
                "score": retUnit.score
            })
    # [
    #     {
    #         "smiles": smiles,
    #         "ret" : {
    #               "category": tables,
    #         }
    #     }
    # ]
    ctx = [{
        "smiles": PredictionResultSmilesInfoTable([smilesDict[index]]),
        "result": dict((PREDICTION_CATEGORY_NAME_DICT.get(category), PredictionResultTable(tables))
                       for category, result in results.items())
    } for index, results in retDict.items()]
    return ctx


def predict(request):
    if not request.POST:
        return HttpResponseBadRequest()

    inputForm = ADMETModelInputForm(request.POST, request.FILES)

    if not inputForm.is_valid():
        return return400ErrorPage(request, inputForm)
    try:
        preRet, invalidInputList, inputCategorys, smilesDict = processADMET(request, inputForm)
    except CommonException as e:
        return HttpResponseBadRequest(e.message)

    if len(request.FILES) == 0:
        preRetTables = _formatRetTables(preRet, inputCategorys, smilesDict)
        retDict = {
            "backURL": reverse('prediction_index'),
            "pageTitle": "Prediction Result"
        }
        if preRetTables:
            retDict['preRetTables'] = preRetTables
        # just for network based
        if invalidInputList and len(invalidInputList) > 0:
            retDict['invalidInputTable'] = InvalidInputsTable.getInvalidInputsTable(invalidInputList)
        return render(request, "preResult.html", retDict)
    else:
        retBook = _formatRetExcelBook(preRet, invalidInputList)
        return make_response(retBook, file_type='csv',
                             file_name=f'ADMET_PredictionResult')


def predictionIndex(request):
    return render(request, 'input.html', INPUT_TEMPLATE_FORMS.get(PREDICTION_TYPE_ADMET))
