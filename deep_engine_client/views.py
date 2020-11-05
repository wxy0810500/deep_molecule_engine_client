# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect

from prediction.forms import ADMETModelInputForm
from prediction.predictionTask import PREDICTION_TYPE_ADMET

INPUT_TEMPLATE_FORMS = {
    PREDICTION_TYPE_ADMET: {
        'inputForm': ADMETModelInputForm(),
        "pageTitle": "admet",
    }
}


def index(request):
    return render(request, 'index.html', INPUT_TEMPLATE_FORMS.get(PREDICTION_TYPE_ADMET))
