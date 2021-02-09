# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect

from prediction.forms import TFModelInputForm
from prediction.predictionTask import PREDICTION_TYPE_TF

INPUT_TEMPLATE_FORMS = {
    PREDICTION_TYPE_TF: {
        'inputForm': TFModelInputForm(),
        "pageTitle": "target fishing",
    }
}


def index(request):
    return render(request, 'index.html', INPUT_TEMPLATE_FORMS.get(PREDICTION_TYPE_TF))
