# -*- coding: utf-8 -*-

from typing import Dict, List

from django.http import HttpResponseBadRequest
from django.shortcuts import reverse
from django_excel import make_response
from pyexcel import Book
import pandas as pd
from django.db.models import QuerySet

from deep_engine_client.exception import *
from deep_engine_client.tables import InvalidInputsTable
from .forms import *
from .predictionTask import PredictionTaskRet
from .service import processTF
from .tables import *


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


def __formatRetTables(preRetList: List[Dict[str, PredictionTaskRet]], validPerformanceDict: Dict,
                      smilesDict: Dict[int, str], inputCategorys: List[str]):
    """

    @param preRetList:
    @param smilesDict:
    @return:
    """
    # tables for each smiles
    # {
    #     smilesIndex: {
    #         category:[
    #             {
    #                 "model":modelName,
    #                 "score": score,
    #                 "geneName":,
    #                 "geneSymbol":,
    #                 "performance":,
    #                 "diseaseClasses":
    #             }
    #         ],
    #     }
    # }

    # result filter: prediction-score>=0.5
    # sort: performance 列
    retDict = dict((smilesIndex, dict((category, []) for category in inputCategorys))
                   for smilesIndex in smilesDict.keys())
    for preRet in preRetList:
        for modelType, preRetRecord in preRet.items():
            performance = validPerformanceDict.get(modelType, None)
            if performance is None:
                continue
            category = performance.category
            for preRetUnit in preRetRecord.preResults:
                smilesIndex: int = int(preRetUnit.sampleId)
                retDict[smilesIndex][category].append({
                    "score": "%.4f" % preRetUnit.score,
                    "model": modelType,
                    "geneName": performance.geneName,
                    "geneSymbol": performance.geneSymbol,
                    "performance": performance.performance,
                    "diseaseClasses": performance.diseaseClass,
                })

    ctx = []
    for index, results in retDict.items():
        ctx.append(
            {
                "smilesTable": PredictionResultSmilesInfoTable([smilesDict[index]]),
                "cleanedSmiles": smilesDict[index]["cleaned_smiles"],
                "result": dict((category, PredictionResultTable(sorted(retOfCategory, key=lambda x: x.get('performance'),
                                                                       reverse=True)))
                               for category, retOfCategory in results.items())
            }
        )
    return ctx


def predict(request):
    if not request.POST:
        return HttpResponseBadRequest()

    inputForm = TFModelInputForm(request.POST, request.FILES)

    if not inputForm.is_valid():
        return return400ErrorPage(request, inputForm)
    try:
        preRet, invalidInputList, validPerformanceDict, smilesDict, inputCategorys = processTF(request, inputForm)
    except CommonException as e:
        return HttpResponseBadRequest(e.message)

    outputType = inputForm.cleaned_data['outputType']
    if outputType == CommonInputForm.OUTPUT_TYPE_WEB_PAGE:
        retDict = {
            "backURL": reverse('main'),
            "pageTitle": "Prediction Result"
        }
        if preRet is not None:
            preRetTables = __formatRetTables(preRet, validPerformanceDict, smilesDict, inputCategorys)
            retDict['preRetTables'] = preRetTables
        # just for network based
        if invalidInputList and len(invalidInputList) > 0:
            retDict['invalidInputTable'] = InvalidInputsTable.getInvalidInputsTable(invalidInputList)
        return render(request, "result.html", retDict)
    else:
        retBook = __formatRetExcelBook(preRet, validPerformanceDict, invalidInputList)
        return make_response(retBook, file_type='csv',
                             file_name=f'TargetFishing_PredictionResult')
