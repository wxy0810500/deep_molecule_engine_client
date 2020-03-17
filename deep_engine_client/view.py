# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from .tables import SmilesResultTable
from .predictionTask import predictSmiles
from .forms import *
from io import BytesIO
from zipfile import ZipFile
import re


SMILES_SEPARATOR_RX = ' |!|,|;|\t|\n'
MAX_SMILES_LEN: int = 150


def index(request):
    return render(request, "input.html", {"textForm": TextInputForm(), "fileForm": FileUploadForm()})


def inputText(request):
    if request.POST:
        form = TextInputForm(request.POST)
        if not form.is_valid():
            return HttpResponse("input data is invalid")

        inputSmiles = form.cleaned_data['t_smiles']
        modelTypes = form.cleaned_data['modelTypes']
        if inputSmiles is None:
            return HttpResponse("input smiles are empty!")

        smilesList = re.split(SMILES_SEPARATOR_RX, inputSmiles.strip())
        smilesList = [smiles for smiles in smilesList if len(smiles) < MAX_SMILES_LEN]
        preRet = predictSmiles(modelTypes, smilesList)
        ctx = []
        for modelType, preRetRecord in preRet.items():
            modelCtx = {'modelType': modelType,
                        'time': 'time = %0.2fs' % preRetRecord.taskTime}
            rlt = [{"id": preRetUnit.sampleId,
                    "label": preRetUnit.label,
                    "ratings": preRetUnit.ratings,
                    "smiles": preRetUnit.smiles}
                   for preRetUnit in preRetRecord.preResults]
            modelCtx['tables'] = SmilesResultTable(rlt)
            ctx.append(modelCtx)
        return render(request, "result.html", {"retTables": ctx})
    else:
        return HttpResponse("invalid http method")


def uploadFile(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponse("no files for upload or no model types selected")
        smiles = handle_uploaded_file(request.FILES['f_smiles'])
        modelTypes = form.cleaned_data['modelTypes']
        smilesList = re.split(SMILES_SEPARATOR_RX, smiles)

        preRet = predictSmiles(modelTypes, smilesList)
        # 每个文件写入到一个csv中，最终写入zip中
        outputZipIO = BytesIO()
        outputZip = ZipFile(outputZipIO, "a")

        for modelType, preRetRecord in preRet.items():
            csvContent = 'modelType:%s\nAll done, time = %0.2fs\nerr_code, result, smiles\n%s' \
                         % (modelType, preRetRecord.taskTime,
                            "\n".join(["{},{},{}".format(preRetUnit.err_code, preRetUnit.result, preRetUnit.smiles)
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


