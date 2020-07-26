from django.shortcuts import render, reverse
from deep_engine_client.sysConfig import *
from .service import *
from .tables import SearchResultTable
from django.http import HttpResponse

# Create your views here.
INPUT_TEMPLATE_FORMS = {
    SERVICE_TYPE_SEARCH: {
        "finished": True,
        'inputForm': TextInputForm(),
        'actionURL': SERVICE_TYPE_SEARCH,
        'specialClass': "search-page",
        'sStatus': "active",
        "pageTitle": "Advanced Search"
    }
}


def searchIndex(request):
    return render(request, 'input.html', INPUT_TEMPLATE_FORMS.get(SERVICE_TYPE_SEARCH))


def advancedSearch(request):
    if request.method != 'POST':
        return HttpResponse('invalid http method')

    inputForm = TextInputForm(request.POST)
    if not inputForm.is_valid():
        return HttpResponse(status=400)
    inputType = inputForm.cleaned_data['inputType']
    inputStr = inputForm.cleaned_data['inputStr']

    csRetDF, scaffoldsRetDF = doAdvancedSearch(inputType, inputStr)

    ret = {
        "exactMapTable": SearchResultTable(csRetDF.to_dict(orient='record')),
        "scaffoldMapTable": SearchResultTable(scaffoldsRetDF.to_dict(orient='record')),
        "backURL": reverse('search_index'),
        "pageTitle": "Search Result"
    }

    return render(request, 'searchResult.html', ret)
