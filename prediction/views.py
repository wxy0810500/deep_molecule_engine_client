# -*- coding: utf-8 -*-from typing import Dict, Listfrom django.http import HttpResponseBadRequestfrom django.shortcuts import reversefrom django_excel import make_responsefrom pyexcel import Bookfrom deep_engine_client.exception import *from deep_engine_client.tables import InvalidInputsTablefrom .forms import *from .predictionTask import PredictionTaskRetfrom .service import processSBVSfrom .tables import *def _formatRetExcelBook(preRetList: List[Dict[str, PredictionTaskRet]], invalidInputList):    sheets = {}    headers = ['', 'Score', 'Input{name|smiles}', 'DrugName', 'CleanedSmiles']    if preRetList is not None and len(preRetList) > 0:        sheetDict = {modelType: [headers] for modelType in preRetList[0].keys()}        for preRet in preRetList:            for modelType, preRetRecord in preRet.items():                records = [[sid + 1,  # id                            '%0.4f' % preRetUnit.score if preRetUnit.score >= 0 else None,  # score                            preRetUnit.input,  # input                            preRetUnit.drugName,  # "drugName":                            preRetUnit.cleanedSmiles]  # "cleanedSmiles":                           for sid, preRetUnit in enumerate(preRetRecord.preResults)]                sheetDict[modelType] += records        sheets = sheetDict    if invalidInputList and len(invalidInputList) > 0:        sheets['invalidInputs'] = [[invalidInput] for invalidInput in invalidInputList]    return Book(sheets)def __formatRetTables(preRetList: List[Dict[str, PredictionTaskRet]]):    if preRetList is None or len(preRetList) == 0:        return None    ctxDict = {modelType: [] for modelType in preRetList[0].keys()}    for preRet in preRetList:        for modelType, preRetRecord in preRet.items():            rlt = [{"id": sid + 1,                    "score": '%0.4f' % preRetUnit.score if preRetUnit.score >= 0 else None,                    "input": preRetUnit.input,                    "drugName": preRetUnit.drugName,                    "cleanedSmiles": preRetUnit.cleanedSmiles}                   for sid, preRetUnit in enumerate(preRetRecord.preResults)]            ctxDict[modelType] += rlt    ctx = [{'modelType': modelType, 'tables': PredictionResultTable(rlt)} for modelType, rlt in ctxDict.items()]    return ctxdef predict(request):    if not request.POST:        return HttpResponseBadRequest()    inputForm = StructureModelInputForm(request.POST, request.FILES)    if not inputForm.is_valid():        return return400ErrorPage(request, inputForm)    try:        preRetList, invalidInputList = processSBVS(request, inputForm)    except CommonException as e:        return HttpResponseBadRequest(e.message)    outputType = inputForm.cleaned_data['outputType']    if outputType == CommonInputForm.OUTPUT_TYPE_WEB_PAGE:        retDict = {            "backURL": reverse('main'),            "pageTitle": "Prediction Result"        }        if preRetList is not None:            preRetTables = __formatRetTables(preRetList)            retDict['preRetTables'] = preRetTables        # just for network based        if invalidInputList and len(invalidInputList) > 0:            retDict['invalidInputTable'] = InvalidInputsTable.getInvalidInputsTable(invalidInputList)        return render(request, "preResult.html", retDict)    else:        retBook = _formatRetExcelBook(preRetList, invalidInputList)        return make_response(retBook, file_type='csv',                             file_name=f'SBVS_PredictionResult')