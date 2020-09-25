# -*- coding: utf-8 -*-

from django.shortcuts import reverse
from django.http import HttpResponseBadRequest

from .service import processADMET
from .tables import *
from .predictionTask import PredictionTaskRet
from .forms import *
from deep_engine_client.sysConfig import *
from typing import Dict
from deep_engine_client.exception import *
from deep_engine_client.tables import InvalidInputsTable
from pyexcel import Book
from django_excel import make_response
import pandas as pd
from typing import Dict, List

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


def _formatRetTables(preRet: Dict[str, PredictionTaskRet]):
    ctx = []
    for modelType, preRetRecord in preRet.items():
        modelCtx = {'modelType': modelType,
                    'time': 'time = %0.2fs' % preRetRecord.taskTime}

        rlt = [{"id": sid + 1,
                "score": '%0.4f' % preRetUnit.score if preRetUnit.score >= 0 else None,
                "input": preRetUnit.input,
                "drugName": preRetUnit.drugName,
                "cleanedSmiles": preRetUnit.cleanedSmiles}
               for sid, preRetUnit in enumerate(preRetRecord.preResults)]
        modelCtx['tables'] = PredictionResultTable(rlt)
        ctx.append(modelCtx)
    return ctx


def _formatNetworkExcelBook(preRetDF: pd.DataFrame, rawRetDF: pd.DataFrame, invalidInputList: pd.DataFrame):
    sheets = {}
    if preRetDF is not None:
        rows = [preRetDF.columns] + preRetDF.values.tolist()
        # preRetDF.astype(dtype='O')
        # rows = [preRetDF.columns] + preRetDF.to_numpy()
        sheets['network_prediction'] = rows

    if rawRetDF is not None:
        rows = [rawRetDF.columns] + rawRetDF.values.tolist()
        sheets['network_raw'] = rows
    if invalidInputList and len(invalidInputList) > 0:
        sheets['invalidInputs'] = [[invalidInput] for invalidInput in invalidInputList]
    return Book(sheets)


def _formatNetworkRetTables(preRetDF: pd.DataFrame, rawRetDF: pd.DataFrame):
    # predicion table:
    retDictList: List[Dict] = preRetDF.to_dict('records')
    # 排除input,drug_name, cleaned_smiles三个字段
    preRetCtx = []
    i = 1
    for columnName in preRetDF.columns[3:]:
        dataDictList = [{
            "input": rowDict.get('input'),
            "drugName": rowDict.get('drug_name'),
            "cleanedSmiles": rowDict.get('cleaned_smiles'),
            'score': rowDict.get(columnName)
        } for rowDict in retDictList]

        modelCtx = {
            'virusName': f'{i}.{columnName}',
            "tables": NetworkBasedResultTable(dataDictList)
        }
        i += 1
        preRetCtx.append(modelCtx)
    # raw
    retDictList: List[Dict] = rawRetDF.to_dict('records')
    # 排除input,drug_name, cleaned_smiles三个字段
    rawRetCtx = []
    i = 1
    for columnName in rawRetDF.columns[3:]:
        dataDictList = [{
            "input": rowDict.get('input'),
            "drugName": rowDict.get('drug_name'),
            "cleanedSmiles": rowDict.get('cleaned_smiles'),
            'score': rowDict.get(columnName)
        } for rowDict in retDictList]

        modelCtx = {
            'virusName': f'{i}.{columnName}',
            "tables": NetworkBasedResultTable(dataDictList)
        }
        i += 1
        rawRetCtx.append(modelCtx)

    return preRetCtx, rawRetCtx


def predict(request):
    if not request.POST:
        return HttpResponseBadRequest()

    inputForm = ADMETModelInputForm(request.POST, request.FILES)

    if not inputForm.is_valid():
        return return400ErrorPage(request, inputForm)
    try:
        preRet, invalidInputList = processADMET(request, inputForm)
    except CommonException as e:
        return HttpResponseBadRequest(e.message)
    if len(request.FILES) > 0:
        inputFile = True
        retBook = _formatRetExcelBook(preRet, invalidInputList)
    else:
        inputFile = False
        preRetTables = _formatRetTables(preRet)


    if inputFile:
        return make_response(retBook, file_type='csv',
                             file_name=f'predictionResult')
    else:
        retDict = {
            "backURL": reverse('prediction_index'),
            "pageTitle": "Prediction Result"
        }
        if preRetTables:
            retDict['preRetTables'] = preRetTables
        # just for network based
        if invalidInputList and len(invalidInputList) > 0:
            retDict['invalidInputTable'] = InvalidInputsTable.getInvalidInputsTable(invalidInputList)
        return render(request, retTemplate, retDict)


def predictionIndex(request):
    return render(request, 'input.html', INPUT_TEMPLATE_FORMS.get(PREDICTION_TYPE_ADMET))
