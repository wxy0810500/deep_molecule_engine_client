# -*- coding: utf-8 -*-

from django.shortcuts import reverse
from django.http import HttpResponseBadRequest

from .service import processLigand, processStructure, processNetWork
from .tables import *
from .predictionTask import PredictionTaskRet
from .forms import *
from deep_engine_client.sysConfig import *
from deep_engine_client.exception import *
from deep_engine_client.tables import InvalidInputsTable
from pyexcel import Book
from django_excel import make_response
import pandas as pd
from typing import Dict, List

INPUT_TEMPLATE_FORMS = {
    PREDICTION_TYPE_LIGAND: {
        'inputForm': LigandModelInputForm(),
        'plStatus': "active",
        "pageTitle": "Ligand Based",
    },
    PREDICTION_TYPE_STRUCTURE: {
        'inputForm': StructureModelInputForm(),
        'psStatus': "active",
        "pageTitle": "Structure Based",
    },
    PREDICTION_TYPE_NETWORK: {
        'inputForm': NetworkModelInputForm(),
        'pnStatus': "active",
        "pageTitle": "Network Based",
    }
}


def __formatRetExcelBook(preRetList: List[Dict[str, PredictionTaskRet]], invalidInputList):
    sheets = {}
    headers = ['', 'Score', 'Input{name|smiles}', 'DrugName', 'CleanedSmiles']
    if preRetList is not None and len(preRetList) > 0:
        sheetDict = {modelType: [headers] for modelType in preRetList[0].keys()}
        for preRet in preRetList:
            for modelType, preRetRecord in preRet.items():
                records = [[sid + 1,  # id
                            '%0.4f' % preRetUnit.score if preRetUnit.score >= 0 else None,  # score
                            preRetUnit.input,  # input
                            preRetUnit.drugName,  # "drugName":
                            preRetUnit.cleanedSmiles]  # "cleanedSmiles":
                           for sid, preRetUnit in enumerate(preRetRecord.preResults)]
                rows = [['time = %0.2fs' % preRetRecord.taskTime], headers] + records
                sheetDict[modelType] = rows
        sheets = sheetDict
    if invalidInputList and len(invalidInputList) > 0:
        sheets['invalidInputs'] = [[invalidInput] for invalidInput in invalidInputList]
    return Book(sheets)


def __formatRetTables(preRetList: List[Dict[str, PredictionTaskRet]]):
    if preRetList is None or len(preRetList) == 0:
        return None
    ctxDict = {modelType: [] for modelType in preRetList[0].keys()}

    for preRet in preRetList:
        for modelType, preRetRecord in preRet.items():
            rlt = [{"id": sid + 1,
                    "score": '%0.4f' % preRetUnit.score if preRetUnit.score >= 0 else None,
                    "input": preRetUnit.input,
                    "drugName": preRetUnit.drugName,
                    "cleanedSmiles": preRetUnit.cleanedSmiles}
                   for sid, preRetUnit in enumerate(preRetRecord.preResults)]
            ctxDict[modelType] += rlt
    ctx = [{'modelType': modelType, 'tables': PredictionResultTable(rlt)} for modelType, rlt in ctxDict.items()]
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
    if preRetDF is not None:
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
            } for rowDict in retDictList if rowDict.get(columnName) != '']

            modelCtx = {
                'virusName': f'{i}.{columnName}',
                "tables": NetworkBasedResultTable(dataDictList)
            }
            i += 1
            preRetCtx.append(modelCtx)
    else:
        preRetCtx = None

    if rawRetDF is not None:
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
            } for rowDict in retDictList if rowDict.get(columnName) != '']

            modelCtx = {
                'virusName': f'{i}.{columnName}',
                "tables": NetworkBasedResultTable(dataDictList)
            }
            i += 1
            rawRetCtx.append(modelCtx)
    else:
        rawRetCtx = None

    return preRetCtx, rawRetCtx


def predict(request, sType: str):
    if not request.POST:
        return HttpResponseBadRequest()

    if PREDICTION_TYPE_LIGAND == sType:
        inputForm = LigandModelInputForm(request.POST, request.FILES)

        if not inputForm.is_valid():
            return return400ErrorPage(request, inputForm)
        try:
            preRetList, invalidInputList = processLigand(request, inputForm)
        except CommonException as e:
            return HttpResponseBadRequest(e.message)
        if len(request.FILES) > 0:
            retBook = __formatRetExcelBook(preRetList, invalidInputList)
        else:
            preRetTables = __formatRetTables(preRetList)
        retTemplate = 'preResult.html'
    elif PREDICTION_TYPE_STRUCTURE == sType:
        inputForm = StructureModelInputForm(request.POST, request.FILES)
        if not inputForm.is_valid():
            return return400ErrorPage(request, inputForm)
        try:
            preRetList, invalidInputList = processStructure(request, inputForm)
        except CommonException as e:
            return HttpResponseBadRequest(e.message)
        if len(request.FILES) > 1:
            retBook = __formatRetExcelBook(preRetList, invalidInputList)
        else:
            preRetTables = __formatRetTables(preRetList)
        retTemplate = 'preResult.html'

    elif PREDICTION_TYPE_NETWORK == sType:
        inputForm = NetworkModelInputForm(request.POST, request.FILES)

        if not inputForm.is_valid():
            return return400ErrorPage(request, inputForm)
        try:
            preRetDF, rawRetDF, invalidInputList = processNetWork(request, inputForm)
        except CommonException as e:
            return HttpResponseBadRequest(e.message)
        if len(request.FILES) > 0:
            retBook = _formatNetworkExcelBook(preRetDF, rawRetDF, invalidInputList)
        else:
            preRetTables, rawRetTables = _formatNetworkRetTables(preRetDF, rawRetDF)

        retTemplate = 'networkBasedResult.html'
    else:
        return HttpResponseBadRequest()

    outputType = inputForm.cleaned_data['outputType']
    if outputType == CommonInputForm.OUTPUT_TYPE_WEB_PAGE:
        retDict = {
            "backURL": reverse('prediction_index', args=[sType]),
            "pageTitle": "Prediction Result"
        }
        if preRetTables:
            retDict['preRetTables'] = preRetTables
        # just for network based
        if PREDICTION_TYPE_NETWORK == sType and rawRetTables is not None:
            retDict['rawRetTables'] = rawRetTables
        if invalidInputList and len(invalidInputList) > 0:
            retDict['invalidInputTable'] = InvalidInputsTable.getInvalidInputsTable(invalidInputList)
        return render(request, retTemplate, retDict)
    else:
        return make_response(retBook, file_type='csv',
                             file_name=f'{sType}PredictionResult')


def predictionIndex(request, sType: str):
    return render(request, f'{sType}BasedInput.html', INPUT_TEMPLATE_FORMS.get(sType))

# def uploadSmilesByFile(request):
#     if request.method == 'POST':
#         form = StructurePDBFileForm(request.POST, request.FILES)
#         if not form.is_valid():
#             return HttpResponse("no files for upload or no model types selected")
#         smiles = handle_uploaded_file(request.FILES['f_smiles'])
#         modelTypes = form.cleaned_data['modelTypes']
#         smilesList = LigandModelChoicesForm.filterInputSmiles(smiles)
#
#         preRet = predictLigand(modelTypes, smilesList)
#         # 每个文件写入到一个csv中，最终写入zip中
#         outputZipIO = BytesIO()
#         outputZip = ZipFile(outputZipIO, "a")
#
#         for modelType, preRetRecord in preRet.items():
#             csvContent = 'modelType:%s\n time = %0.2fs\n score, smiles\n%s' \
#                          % (modelType, preRetRecord.taskTime,
#                             "\n".join(["%0.4f,%s" % (preRetUnit.score, preRetUnit.smiles)
#                                        for preRetUnit in preRetRecord.preResults])
#                             )
#             outputZip.writestr("{}.csv".format(modelType), csvContent)
#
#         for file in outputZip.filelist:
#             file.create_system = 0
#
#         outputZip.close()
#         outputZipIO.seek(0)
#         response = HttpResponse(outputZipIO, content_type="application/zip")
#         response['Content-Disposition'] = 'attachment;filename="result.zip"'
#
#         return response
#     else:
#         return HttpResponse('invalid http method')
