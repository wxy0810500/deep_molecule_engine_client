# -*- coding: utf-8 -*-

from typing import Dict, List

from django.http import HttpResponseBadRequest
from django.shortcuts import reverse
from django_excel import make_response
from pyexcel import Book

from deep_engine_client.exception import *
from deep_engine_client.tables import InvalidInputsTable
from .forms import *
from .predictionTask import PredictionTaskRet, PREDICTION_TYPE_ADMET
from configuration.sysConfig import PREDICTION_CATEGORY_NAME_DICT, PREDICTION_MODEL_CATEGORY_DICT, \
    PREDICTION_CATEGORYS_IN_RADAR, PREDICTION_CATEGORY_MODEL_DICT
from .service import processADMET
from .tables import *
import numpy as np
import json


def __formatRetExcelBook(preRetList: List[Dict[str, PredictionTaskRet]], invalidInputList):
    sheets = {}
    if preRetList is not None:
        # headers
        headers = ['Input{name|smiles}', 'DrugName', 'CleanedSmiles']
        inputModelTypes = list(preRetList[0].keys())
        headers.extend(inputModelTypes)
        rows = [headers]
        # smilesModelScoreDict = {
        #     smilesIndex : {
        #         input:
        #         drugName:
        #         cleaned_smiles:
        #         modelType1:score1,
        #         modelType2:score2,
        #     }
        # }
        for preRet in preRetList:
            # 从preRet中任意拿出一个preRetRecord，均包含所有的input信息，用于初始化下列dict
            smilesModelScoreDict = dict((int(preRetUnit.sampleId), {
                "input": preRetUnit.input,
                "drugName": preRetUnit.drugName,
                "cleanedSmiles": preRetUnit.cleanedSmiles,
            }) for preRetUnit in preRet.get(inputModelTypes[0]).preResults)
            for modelType, preRetRecord in preRet.items():
                for preRetUnit in preRetRecord.preResults:
                    smilesIndex = int(preRetUnit.sampleId)
                    smilesModelScoreDict[smilesIndex][modelType] = preRetUnit.score

            # 根据inputModelType中modelType的顺序rowData
            for smilesIndex, modelScoreDict in smilesModelScoreDict.items():
                rowData = [modelScoreDict.get('input'), modelScoreDict.get("drugName"),
                           modelScoreDict.get("cleanedSmiles")]
                for modelType in inputModelTypes:
                    rowData.append(modelScoreDict.get(modelType))
                rows.append(rowData)
        sheets['predictionResult'] = rows
    if invalidInputList and len(invalidInputList) > 0:
        sheets['invalidInputs'] = [[invalidInput] for invalidInput in invalidInputList]
    return Book(sheets)


def _formatRetTables(preRetList: List[Dict[str, PredictionTaskRet]], inputCategorys: List[str],
                     smilesDict: Dict[int, str]):
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
    for preRet in preRetList:
        for modelType, preRetRecord in preRet.items():
            category = PREDICTION_MODEL_CATEGORY_DICT.get(modelType, None)
            if category is None:
                category = "unsupported"
            for preRetUnit in preRetRecord.preResults:
                smilesIndex: int = int(preRetUnit.sampleId)
                retDict[smilesIndex][category].append({
                    "model": modelType,
                    "score": "%.4f" % preRetUnit.score
                })

    # [
    #     {
    #         "smilesTable": smilesTable,
    #         "cleanedSmiles": cleanedSmiles,
    #         "result" : {
    #               "category": tables,
    #         }
    #         "radarData": {
    #           "category": average-score
    #         }
    #     }
    # ]
    def getAverageScoreForEachCategory(resultsOfSingleSmiles):
        averageScoreDict = {}
        for category in PREDICTION_CATEGORYS_IN_RADAR:
            resultsOfCategory = resultsOfSingleSmiles.get(category, None)
            if resultsOfCategory is not None:
                # 雷达图上数值，用1-score之后再求平均值
                aveScore = np.mean(
                    list(
                        map(lambda x: (1 - float(x.get("score"))), resultsOfCategory)
                    )
                )
            else:
                aveScore = 0
            averageScoreDict[category] = '%.4f' % aveScore
        return averageScoreDict

    ctx = [{
        "smilesTable": PredictionResultSmilesInfoTable([smilesDict[index]]),
        "cleanedSmiles": smilesDict[index]["cleaned_smiles"],
        "result": dict((PREDICTION_CATEGORY_NAME_DICT.get(category), PredictionResultTable(result))
                       for category, result in results.items()),
        "radarData": json.dumps(getAverageScoreForEachCategory(results))
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

    outputType = inputForm.cleaned_data['outputType']
    if outputType == CommonInputForm.OUTPUT_TYPE_WEB_PAGE:
        retDict = {
            "backURL": reverse('main'),
            "pageTitle": "Prediction Result"
        }
        if preRet is not None:
            preRetTables = _formatRetTables(preRet, inputCategorys, smilesDict)
            retDict['preRetTables'] = preRetTables
        # just for network based
        if invalidInputList and len(invalidInputList) > 0:
            retDict['invalidInputTable'] = InvalidInputsTable.getInvalidInputsTable(invalidInputList)
        return render(request, "preResult.html", retDict)
    else:
        retBook = __formatRetExcelBook(preRet, invalidInputList)
        return make_response(retBook, file_type='csv',
                             file_name=f'ADMET_PredictionResult')