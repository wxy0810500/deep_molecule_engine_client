# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from .tables import SmilesResultTable
from .predictionTask import predictSmiles
from .forms import *
from _collections import OrderedDict
from pyexcel_io import save_data
from io import StringIO
import re


SMILES_SEPARATOR_RX = ' |!|,|;|\t'


def index(request):
    return render(request, "input.html", {"textForm": TextInputForm(), "fileForm": FileUploadForm()})


def inputText(request):
    if request.POST:
        form = TextInputForm(request.POST)
        if form.is_valid():
            inputSmiles = form.cleaned_data['t-smiles']
            modelTypes = form.cleaned_data['modelTypes']
            if inputSmiles is not None:
                smilesList = re.split(SMILES_SEPARATOR_RX, inputSmiles.strip())
                preRet = predictSmiles(modelTypes, smilesList)
                ctx = []
                for modelType, preRetRecord in preRet.items():
                    modelCtx = {'modelType': modelType,
                                'time': 'All done, time = %0.2fs' % preRetRecord.taskTime,
                                'info': 'Server_info = %s' % preRetRecord.serverInfo}
                    rlt = [{"err_code": preRetUnit.err_code, "result": preRetUnit.result, "SMILES": preRetUnit.smiles}
                           for preRetUnit in preRetRecord.preResults]
                    modelCtx['tables'] = SmilesResultTable(rlt)
                    ctx.append(modelCtx)
                    ctx.append(modelCtx)
                return render(request, "result.html", {"retTables": ctx})
            else:
                return HttpResponse("input smiles are empty!")
        else:
            return HttpResponse("input data is invalid")
    else:
        return HttpResponse("invalid http method")


def uploadFile(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponse("no files for upload!")
        smiles = handle_uploaded_file(request.FILES['f_smiles'])
        modelTypes = form.cleaned_data['modelTypes']
        smilesList = re.split(SMILES_SEPARATOR_RX, smiles)

        preRet = predictSmiles(modelTypes, smilesList)
        # 导出到csv，每个model一个sheet
        # from collections import OrderedDict
        data = OrderedDict()
        for modelType, preRetRecord in preRet.items():
            sheetRows = [['modelType:%s' % modelType],
                         ['All done, time = %0.2fs' % preRetRecord.taskTime],
                         ['Server_info = %s' % preRetRecord.serverInfo],
                         ['err_code', 'result', 'smiles']]
            rlt = [sheetRows.append([preRetUnit.err_code, preRetUnit.result, preRetUnit.smiles])
                   for preRetUnit in preRetRecord.preResults]
            data.update({modelType: sheetRows})

        data.update({"Sheet 1": [[1, 2, 3], [4, 5, 6]]})
        data.update({"Sheet 2": [["row 1", "row 2", "row 3"]]})
        outputIO = StringIO()
        save_data(outputIO, data)
        response = StreamingHttpResponse(outputIO, content_type="text/csv")
        response['Content-Disposition'] = 'attachment;filename="result.csv"'

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


