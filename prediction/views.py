# -*- coding: utf-8 -*-

from django.shortcuts import render, reverse
from django.http import HttpResponseBadRequest

from utils.fileUtils import handle_uploaded_file
from .tables import PredictionResultTable
from .predictionTask import PredictionTaskRet, predictStructure, predictLigand
from .forms import *
from deep_engine_client.sysConfig import *
from typing import Dict, List, Tuple
from deep_engine_client.exception import *
from smiles.searchService import searchDrugReferenceByInputRequest
from deep_engine_client.tables import InvalidInputsTable
from pyexcel import Book
from django_excel import make_response

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
        'finished': False,
        'specialClass': "unfinished-model",
        'pnStatus': "active",
        "pageTitle": "Network Based",
    }
}


def predictionIndex(request, sType: str):
    return render(request, 'input.html', INPUT_TEMPLATE_FORMS.get(sType))


def predict(request, sType: str):
    if not request.POST:
        return HttpResponseBadRequest()

    if PREDICTION_TYPE_LIGAND == sType:
        if len(request.FILES) > 0:
            inputFile = True
            inputForm = LigandModelInputForm(request.POST, request.FILES)
        else:
            inputFile = False
            inputForm = LigandModelInputForm(request.POST)
        if not inputForm.is_valid():
            return return400ErrorPage(request, inputForm)
        try:
            preRet, invalidInputList = processLigand(request, inputForm)
        except CommonException as e:
            return HttpResponseBadRequest(e.message)
    elif PREDICTION_TYPE_STRUCTURE == sType:
        if len(request.FILES) > 1:
            inputFile = True
        else:
            inputFile = False
        inputForm = StructureModelInputForm(request.POST, request.FILES)
        if inputForm.is_valid():
            try:
                preRet, invalidInputList = processStructure(request, inputForm)
            except CommonException as e:
                return HttpResponseBadRequest(e.message)
        else:
            return return400ErrorPage(request, inputForm)
    else:
        return HttpResponseBadRequest()
    if inputFile:
        return make_response(_formatRetExcelBook(preRet, invalidInputList), file_type='csv',
                             file_name=f'{sType}PredictionResult')
    else:
        retDict = {
            "backURL": reverse('prediction_index', args=[sType]),
            "pageTitle": "Prediction Result"
        }
        if preRet:
            retDict['retTables'] = _formatRetTables(preRet)
        if invalidInputList and len(invalidInputList) > 0:
            retDict['invalidInputTable'] = InvalidInputsTable.getInvalidInputsTable(invalidInputList)
        return render(request, "preResult.html", retDict)


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


def _getSmilesInfoListFromInputForm(request, inputForm) -> Tuple[List[dict], List[str]]:
    drugRefDF, invalidInputList = searchDrugReferenceByInputRequest(request, inputForm)
    if drugRefDF.size == 0:
        return None, invalidInputList
    return drugRefDF[['input', 'drug_name', 'cleaned_smiles']].to_dict(orient='records'), invalidInputList


def processLigand(request, inputForm: LigandModelInputForm):
    smilesInfoList, invalidInputList = _getSmilesInfoListFromInputForm(request, inputForm)
    if smilesInfoList:
        modelTypes = inputForm.cleaned_data['modelTypes']
        preRet = predictLigand(modelTypes, smilesInfoList)
    else:
        preRet = None
    return preRet, invalidInputList


def processStructure(request, inputForm: StructureModelInputForm):
    # get smiles
    smilesInfoList, invalidInputList = _getSmilesInfoListFromInputForm(request, inputForm)
    if smilesInfoList:
        # get pdbFile
        pdbContent = handle_uploaded_file(request.FILES['uploadPDBFile'])

        modelTypes = inputForm.cleaned_data['modelTypes']
        preRet = predictStructure(modelTypes, smilesInfoList, pdbContent)
    else:
        preRet = None
    return preRet, invalidInputList

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
