# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse, Http404
from .tables import PredictionResultTable
from .predictionTask import predictLigand, PredictionTaskRet
from .forms import *
from deep_engine_client.sysConfig import *
from io import BytesIO
from zipfile import ZipFile
from typing import Dict, Union, List
from deep_engine_client.exception import *
from smiles.searchService import searchDrugReferenceByTextInputData


INPUT_TEMPLATE_FORMS = {
    PREDICTION_TYPE_LIGAND: {
        'inputForm': LigandModelChoicesForm(),
        'actionURL': f'predict/{SERVICE_TYPE_PREDICTION}'
    },
    PREDICTION_TYPE_STRUCTURE: {
        'inputForm': StructureInputForm(),
        'actionURL': f'predict/{SERVICE_TYPE_PREDICTION}',
        'pdbFileForm': StructurePDBFileForm()
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
            ctx = processLigand(inputForm)
        except PredictionCommonException as e:
            return HttpResponse(e.message)
    return render(request, "result.html", {"retTables": ctx})


def processLigand(inputForm: LigandModelChoicesForm):
    inputType = inputForm.cleaned_data['inputType']
    inputStr = inputForm.cleaned_data['inputStr']
    modelTypes = inputForm.cleaned_data['modelTypes']

    drugRefDF = searchDrugReferenceByTextInputData(inputType, inputStr)
    if drugRefDF is None:
        raise Http404
    s = drugRefDF[['input', 'drug_name', 'cleaned_smiles']]
    smilesDict = drugRefDF[['input', 'drug_name', 'cleaned_smiles']].to_dict(orient='records')
    preRet = predictLigand(modelTypes, smilesDict)

    return formatRetTable(preRet)


def formatRetTable(preRet: Dict[str, PredictionTaskRet]):
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


def uploadFile(request):
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


def handle_uploaded_file(f):
    ret = []
    for chunk in f.chunks():
        ret.append(str(chunk, 'utf-8'))
    return ','.join(ret)


def file_iterator(file, chunk_size=512):
    with open(file) as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break
