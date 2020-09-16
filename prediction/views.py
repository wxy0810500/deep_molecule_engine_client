# -*- coding: utf-8 -*-

from django.shortcuts import reverse
from django.http import HttpResponseBadRequest

from .service import processLigand, processStructure, processNetWork
from .tables import PredictionResultTable
from .predictionTask import PredictionTaskRet
from .forms import *
from deep_engine_client.sysConfig import *
from typing import Dict
from deep_engine_client.exception import *
from deep_engine_client.tables import InvalidInputsTable
from pyexcel import Book
from django_excel import make_response
import pandas as pd
import django_tables2 as tables

INPUT_TEMPLATE_FORMS = {
    PREDICTION_TYPE_LIGAND: {
        'finished': True,
        'inputForm': LigandModelInputForm(),
        'actionURL': f'predict/{SERVICE_TYPE_PREDICTION}',
        'plStatus': "active",
        "pageTitle": "Ligand Based",
    },
    PREDICTION_TYPE_STRUCTURE: {
        'finished': True,
        'inputForm': StructureModelInputForm(),
        'actionURL': f'predict/{SERVICE_TYPE_PREDICTION}',
        'psStatus': "active",
        "pageTitle": "Structure Based",
    },
    PREDICTION_TYPE_NETWORK: {
        'finished': True,
        'inputForm': NetworkModelInputForm(),
        'actionURL': f'predict/{SERVICE_TYPE_PREDICTION}',
        'pnStatus': "active",
        "pageTitle": "Network Based",
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
    ctx = []
    # predicion table:
    modelCtx = {'modelType': 'network based prediction result',
                'tables': tables.Table(preRetDF.to_dict('records'),
                                       extra_columns=[(column, tables.Column(orderable=False))
                                                      for column in preRetDF.columns])}
    ctx.append(modelCtx)
    # raw table
    modelCtx = {'modelType': 'network based raw result',
                'tables': tables.Table(rawRetDF.to_dict('records'),
                                       extra_columns=[(column, tables.Column(orderable=False))
                                                      for column in rawRetDF.columns])}
    ctx.append(modelCtx)
    return ctx


def predict(request, sType: str):
    if not request.POST:
        return HttpResponseBadRequest()

    if PREDICTION_TYPE_LIGAND == sType:
        inputForm = LigandModelInputForm(request.POST, request.FILES)

        if not inputForm.is_valid():
            return return400ErrorPage(request, inputForm)
        try:
            preRet, invalidInputList = processLigand(request, inputForm)
        except CommonException as e:
            return HttpResponseBadRequest(e.message)
        if len(request.FILES) > 0:
            inputFile = True
            retBook = _formatRetExcelBook(preRet, invalidInputList)
        else:
            inputFile = False
            retTables = _formatRetTables(preRet)
    elif PREDICTION_TYPE_STRUCTURE == sType:
        inputForm = StructureModelInputForm(request.POST, request.FILES)
        if not inputForm.is_valid():
            return return400ErrorPage(request, inputForm)

        try:
            preRet, invalidInputList = processStructure(request, inputForm)

        except CommonException as e:
            return HttpResponseBadRequest(e.message)
        if len(request.FILES) > 1:
            inputFile = True
            retBook = _formatRetExcelBook(preRet, invalidInputList)
        else:
            inputFile = False
            retTables = _formatRetTables(preRet)

    elif PREDICTION_TYPE_NETWORK == sType:
        inputForm = NetworkModelInputForm(request.POST, request.FILES)

        if not inputForm.is_valid():
            return return400ErrorPage(request, inputForm)
        try:
            preRetDF, rawRetDF, invalidInputList = processNetWork(request, inputForm)
        except CommonException as e:
            return HttpResponseBadRequest(e.message)
        if len(request.FILES) > 0:
            inputFile = True
            retBook = _formatNetworkExcelBook(preRetDF, rawRetDF, invalidInputList)
        else:
            inputFile = False
            retTables = _formatNetworkRetTables(preRetDF, rawRetDF)
    else:
        return HttpResponseBadRequest()
    if inputFile:
        return make_response(retBook, file_type='csv',
                             file_name=f'{sType}PredictionResult')
    else:
        retDict = {
            "backURL": reverse('prediction_index', args=[sType]),
            "pageTitle": "Prediction Result"
        }
        if retTables:
            retDict['retTables'] = retTables
        if invalidInputList and len(invalidInputList) > 0:
            retDict['invalidInputTable'] = InvalidInputsTable.getInvalidInputsTable(invalidInputList)
        return render(request, "preResult.html", retDict)


def predictionIndex(request, sType: str):
    return render(request, 'input.html', INPUT_TEMPLATE_FORMS.get(sType))

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
