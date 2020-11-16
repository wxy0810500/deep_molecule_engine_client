# -*- coding: utf-8 -*-

from django.shortcuts import render
from prediction.forms import StructureModelInputForm
from prediction.config import PREDICTION_TYPE_STRUCTURE_BASED

INPUT_TEMPLATE_FORMS = {
    PREDICTION_TYPE_STRUCTURE_BASED: {
        'inputForm': StructureModelInputForm(),
        "pageTitle": "SBVS",
    }
}


def index(request):
    return render(request, 'index.html', INPUT_TEMPLATE_FORMS.get(PREDICTION_TYPE_STRUCTURE_BASED))
