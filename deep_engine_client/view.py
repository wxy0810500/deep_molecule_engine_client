# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .tables import SmilesResultTable
from .predictionTask import predictSmiles
from .forms import *
from .sysConfig import *
from io import BytesIO
from zipfile import ZipFile
import re

SMILES_SEPARATOR_RX = '!|,|;|\t|\n|\r\n'
MAX_SMILES_LEN: int = 500


def tempRoot(request):
    return redirect('/covid19')


def index(request):
    return predictIndex(request)


INPUT_TEMPLATE_FORMS = {
    PREDICTION_TYPE_LIGAND: {
        'inputForm': LigandModelChoicesForm(),
        'serviceType': SERVICE_TYPE_PREDICTION
    },
    PREDICTION_TYPE_STRUCTURE: {
        'inputForm': StructureModelChoicesForm(),
        'pdbFileForm': StructurePdbFileUploadForm(),
        'serviceType': SERVICE_TYPE_PREDICTION
    },
    SERVICE_TYPE_SEARCH: {
        'inputForm': TextInputForm(),
        'serviceType': SERVICE_TYPE_SEARCH
    }
}


def predictIndex(request, sType: str):
    return render(request, 'input.html', INPUT_TEMPLATE_FORMS.get(sType))


def filterInputSmiles(smiles: str):
    smilesList = re.split(SMILES_SEPARATOR_RX, smiles.strip())
    return [smiles.strip() for smiles in smilesList if (MAX_SMILES_LEN > len(smiles) > 0)]


def inputSmilesOrNames(request):
    pass


def processInputSmiles(request, mCategory: str):
    if request.POST:
        form = TextInputForm(request.POST)
        if not form.is_valid():
            return HttpResponse("input data is invalid")

        inputSmiles = form.cleaned_data['t_smiles']
        modelTypes = form.cleaned_data['modelTypes']
        if inputSmiles is None:
            return HttpResponse("input smiles are empty!")

        smilesList = filterInputSmiles(inputSmiles)
        preRet = predictSmiles(modelTypes, smilesList, None)
        if preRet is None:
            return HttpResponse("We will support these model types as soon as possible!")
        ctx = []
        for modelType, preRetRecord in preRet.items():
            modelCtx = {'modelType': modelType,
                        'time': 'time = %0.2fs' % preRetRecord.taskTime}

            rlt = [{"id": sid + 1,
                    "score": '%0.4f' % preRetUnit.score if preRetUnit.score >= 0 else None,
                    "smiles": preRetUnit.smiles}
                   for sid, preRetUnit in enumerate(preRetRecord.preResults)]
            modelCtx['tables'] = SmilesResultTable(rlt)
            ctx.append(modelCtx)
        return render(request, "result.html", {"retTables": ctx})
    else:
        return HttpResponse("invalid http method")


def uploadFile(request):
    if request.method == 'POST':
        form = StructurePdbFileUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponse("no files for upload or no model types selected")
        smiles = handle_uploaded_file(request.FILES['f_smiles'])
        modelTypes = form.cleaned_data['modelTypes']
        smilesList = filterInputSmiles(smiles)

        preRet = predictSmiles(modelTypes, smilesList)
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
