# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from django.http import StreamingHttpResponse

from deep_engine_client.dme.client import DME_client
import pandas as pds
import csv
import re
from tempfile import TemporaryFile
from .forms import UploadFileForm
from django.views.decorators import csrf
import argparse, os
# os.environ['MP_NUM_THREADS=1'] = 1


dme_server_host = "192.168.16.186"
dme_server_port = 6000

SMILES_SEPARATOR_RX = ' |!|.|;|\t'


def index(request):
    return render(request, "input.html")


def smiles(request):
    ctx = {}
    if request.POST:
        smiles = request.POST['q-smiles']
        if smiles is not None:
            smilesList = re.split(SMILES_SEPARATOR_RX, smiles)
            # --- make client ---#
            client = DME_client()
            client_worker = client.make_worker(dme_server_host, dme_server_port, time_out=10)
            results, err_codes, task_time, server_info = client.do_task(client_worker, smilesList)
            smilesRlt = ''
            for SMILES, result, err_code in zip(smilesList, results, err_codes):
                smilesRlt += '%d, %s, %s <br>' % (err_code, result, SMILES)

            rlt = 'All done, time = %0.2fs<br>Server_info = %s<br>%s' % (task_time, server_info, smilesRlt)
            # smilesRet = '\n'.join(smileslist)
            # rlt = 'All done, time = %0.2fs\nServer_info = %s\n%s' % (10, 'server_info', smilesRet)
    else:
        rlt = "invalid http method"
    ctx['rlt'] = rlt
    return render(request, "result.html", ctx)


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def upload(request):

    if request.method == 'POST':
        uploadFile = request.FILES.get("f-smiles", None)
        if uploadFile is None:
            return HttpResponse("no files for upload!")
        smiles = handle_uploaded_file(uploadFile)
        pds.read_excel()
        smileslist = re.split(SMILES_SEPARATOR_RX, smiles)

        #--- make client ---#
        client = DME_client()
        client_worker = client.make_worker(dme_server_host, dme_server_port, time_out=10)
        results, err_codes, task_time, server_info = client.do_task(client_worker, smileslist)

        rows = ([err_code, result, SMILES]
                for SMILES, result, err_code in zip(smileslist, results, err_codes))
        # rows = ([10, 'true', str(t_smiles)] for t_smiles in smileslist)

        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                         content_type="text/csv")
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



