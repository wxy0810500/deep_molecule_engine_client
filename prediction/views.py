# -*- coding: utf-8 -*-

from django.shortcuts import render, reverse
from django.http import HttpResponse

from utils.fileUtils import handle_uploaded_file
from .tables import PredictionResultTable
from .predictionTask import predictLigand, predictStructure, PredictionTaskRet
from .forms import *
from deep_engine_client.sysConfig import *
from io import BytesIO
from zipfile import ZipFile
from typing import Dict, List, Tuple
from deep_engine_client.exception import *
from smiles.searchService import searchDrugReferenceByTextInputData
from deep_engine_client.tables import InvalidInputsTable


INPUT_TEMPLATE_FORMS = {
    PREDICTION_TYPE_LIGAND: {
        'finished': True,
        'inputForm': LigandModelChoicesForm(),
        'actionURL': f'predict/{SERVICE_TYPE_PREDICTION}',
        'plStatus': "active",
        "pageTitle": "Ligand Based",
    },
    PREDICTION_TYPE_STRUCTURE: {
        'finished': True,
        'inputForm': StructureInputForm(),
        'actionURL': f'predict/{SERVICE_TYPE_PREDICTION}',
        'pdbFileForm': StructurePDBFileForm(),
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
        return HttpResponse(status=400)

    if PREDICTION_TYPE_LIGAND == sType:
        inputForm = LigandModelChoicesForm(request.POST)
        if not inputForm.is_valid():
            return HttpResponse(status=400)
        try:
            retTables, invalidInputList = processLigand(inputForm)
        except PredictionCommonException as e:
            return HttpResponse(e.message)
    elif PREDICTION_TYPE_STRUCTURE == sType:
        inputForm = StructureInputForm(request.POST)
        pdbForm = StructurePDBFileForm(request.POST, request.FILES)
        if inputForm.is_valid() and pdbForm.is_valid():
            try:
                retTables, invalidInputList = processStructure(request, inputForm)
            except PredictionCommonException as e:
                return HttpResponse(e.message)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)

    retDict = {
                  "backURL": reverse('prediction_index', args=[sType]),
                  "pageTitle": "Prediction Result"
              }
    if retTables:
        retDict['retTables'] = retTables
    if invalidInputList and len(invalidInputList) > 0:
        retDict['invalidInputTable'] = InvalidInputsTable.getInvalidInputsTable(invalidInputList)
    return render(request, "preResult.html", retDict)


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


def _getSmilesInfoListFromTextInputForm(inputForm: TextInputForm) -> Tuple[List[dict], List[str]]:
    inputType = inputForm.cleaned_data['inputType']
    inputStr = inputForm.cleaned_data['inputStr']

    drugRefDF, invalidInputList = searchDrugReferenceByTextInputData(inputType, inputStr)
    if drugRefDF.size == 0:
        return None, invalidInputList
    return drugRefDF[['input', 'drug_name', 'cleaned_smiles']].to_dict(orient='records'), invalidInputList


def processLigand(inputForm: LigandModelChoicesForm):
    smilesInfoList, invalidInputList = _getSmilesInfoListFromTextInputForm(inputForm)
    if smilesInfoList:
        modelTypes = inputForm.cleaned_data['modelTypes']
        preRet = predictLigand(modelTypes, smilesInfoList)
        retTables = _formatRetTables(preRet)
    else:
        retTables = None
    return retTables, invalidInputList


def processStructure(request, inputForm: StructureInputForm):
    # get smiles
    smilesInfoList, invalidInputList = _getSmilesInfoListFromTextInputForm(inputForm)
    if smilesInfoList:
        # get pdbFile
        pdbContent = handle_uploaded_file(request.FILES['uploadFile'])

        modelTypes = inputForm.cleaned_data['modelTypes']
        preRet = predictStructure(modelTypes, smilesInfoList, pdbContent)
        retTables = _formatRetTables(preRet)
    else:
        retTables = None
    return retTables, invalidInputList


def uploadSmilesByFile(request):
    if request.method == 'POST':
        form = StructurePDBFileForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponse("no files for upload or no model types selected")
        smiles = handle_uploaded_file(request.FILES['f_smiles'])
        modelTypes = form.cleaned_data['modelTypes']
        smilesList = LigandModelChoicesForm.filterInputSmiles(smiles)

        preRet = predictLigand(modelTypes, smilesList)
        # 每个文件写入到一个csv中，最终写入zip中
        outputZipIO = BytesIO()
        outputZip = ZipFile(outputZipIO, "a")

        for modelType, preRetRecord in preRet.items():
            csvContent = 'modelType:%s\n time = %0.2fs\n score, smiles\n%s' \
                         % (modelType, preRetRecord.taskTime,
                            "\n".join(["%0.4f,%s" % (preRetUnit.score, preRetUnit.smiles)
                                       for preRetUnit in preRetRecord.preResults])
                            )
            outputZip.writestr("{}.csv".format(modelType), csvContent)

        for file in outputZip.filelist:
            file.create_system = 0

        outputZip.close()
        outputZipIO.seek(0)
        response = HttpResponse(outputZipIO, content_type="application/zip")
        response['Content-Disposition'] = 'attachment;filename="result.zip"'

        return response
    else:
        return HttpResponse('invalid http method')
