from django.shortcuts import render
from django.http import HttpResponse
from deep_engine_client.forms import *
from deep_engine_client.sysConfig import *

# Create your views here.
INPUT_TEMPLATE_FORMS = {
    SERVICE_TYPE_SEARCH: {
        'inputForm': TextInputForm(),
        'actionURL': SERVICE_TYPE_SEARCH
    }
}


def searchIndex(request):
    return render(request, 'input.html', INPUT_TEMPLATE_FORMS.get(SERVICE_TYPE_SEARCH))


def advancedSearch(request):
    return HttpResponse("advanced search")
