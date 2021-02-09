# -*- coding: utf-8 -*-

from typing import Dict, List

from django.http import HttpResponseBadRequest
from django.shortcuts import reverse
from django_excel import make_response
from pyexcel import Book

from deep_engine_client.exception import *
from deep_engine_client.tables import InvalidInputsTable
from .forms import *
from .predictionTask import PredictionTaskRet
from configuration.sysConfig import PREDICTION_CATEGORY_NAME_DICT, PREDICTION_MODEL_CATEGORY_DICT, \
    PREDICTION_CATEGORYS_IN_RADAR, AverageOperation_IN_RADAR_DICT
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
                continue
            for preRetUnit in preRetRecord.preResults:
                smilesIndex: int = int(preRetUnit.sampleId)
                aveOptDict = AverageOperation_IN_RADAR_DICT.get(category)
                aveOperatedScore = 0
                if aveOptDict is not None:
                    aveOpt = aveOptDict.get(modelType)
                    if aveOpt is not None:
                        aveOperatedScore = float(preRetUnit.score) * aveOpt
                    else:
                        print(f'{category}_{modelType}')
                # aveOperatedScore = float(preRetUnit.score) * aveOptDict.get(modelType) if aveOptDict is not None else 0
                retDict[smilesIndex][category].append({
                    "model": modelType if aveOperatedScore != 0 else f"{modelType} *",
                    "score": "%.4f" % preRetUnit.score,
                    "scoreForAve":
                        float('%.4f' % (
                            aveOperatedScore + 1 if aveOperatedScore < 0 else aveOperatedScore))
                        if aveOperatedScore != 0 else ""
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
                    [ret.get('scoreForAve') for ret in resultsOfCategory if ret.get('scoreForAve') != ""]
                )
                aveScore = float('%.4f' % aveScore)
            else:
                aveScore = 0
            averageScoreDict[PREDICTION_CATEGORY_NAME_DICT.get(category)] = aveScore
        return averageScoreDict

    ctx = []
    for index, results in retDict.items():
        aveScoreDict = getAverageScoreForEachCategory(results)
        ctx.append(
            {
                "smilesTable": PredictionResultSmilesInfoTable([smilesDict[index]]),
                "cleanedSmiles": smilesDict[index]["cleaned_smiles"],
                "result": dict((PREDICTION_CATEGORY_NAME_DICT.get(category),
                                PredictionResultTable(sorted(result, key=lambda x: x.get("model"))))
                               for category, result in results.items()),
                "radarData": json.dumps(aveScoreDict),
                "druglikeScore": "%.4f" % np.mean([s for s in aveScoreDict.values() if s > 0])
            }
        )
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
