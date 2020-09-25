from django.shortcuts import render, reverse
from deep_engine_client.sysConfig import *
from .service import *
from .tables import SearchResultTable
from django.http import HttpResponse
from deep_engine_client.exception import return400ErrorPage
from deep_engine_client.tables import InvalidInputsTable
from django_excel import make_response
from pyexcel import Book

# Create your views here.
INPUT_TEMPLATE_FORMS = {
    SERVICE_TYPE_SEARCH: {
        'inputForm': CommonInputForm(),
        'specialClass': "search-page",
        'sStatus': "active",
        "pageTitle": "Advanced Search"
    }
}


def searchIndex(request):
    return render(request, 'searchInput.html', INPUT_TEMPLATE_FORMS.get(SERVICE_TYPE_SEARCH))


def advancedSearch(request):
    if request.method != 'POST':
        return HttpResponse('invalid http method')
    if len(request.FILES) > 0:
        inputFile = True
        inputForm = CommonInputForm(request.POST, request.FILES)
    else:
        inputFile = False
        inputForm = CommonInputForm(request.POST)
    if not inputForm.is_valid():
        return return400ErrorPage(request, inputForm)()

    csRetDF, scaffoldsRetDF, invalidInputList = doAdvancedSearch(request, inputForm)
    if inputFile:
        ret = {}
        if csRetDF is not None:
            ret["exactMap"] = [csRetDF.columns.to_list()] + list(csRetDF.to_numpy())
        if scaffoldsRetDF is not None:
            ret["scaffoldMapTable"] = [scaffoldsRetDF.columns.to_list()] + list(scaffoldsRetDF.to_numpy())
        if invalidInputList and len(invalidInputList) > 0:
            ret["invalidInputTable"] = [[invalidInput] for invalidInput in invalidInputList]

        return make_response(Book(ret), file_type='xls', file_name="advancedSearchResult")
    else:
        ret = {
            "backURL": reverse('search_index'),
            "pageTitle": "Search Result"
        }
        if csRetDF is not None:
            ret["exactMapTable"] = SearchResultTable(csRetDF.to_dict(orient='record'))
        if scaffoldsRetDF is not None:
            ret["scaffoldMapTable"] = SearchResultTable(scaffoldsRetDF.to_dict(orient='record'))
        if invalidInputList and len(invalidInputList) > 0:
            ret["invalidInputTable"] = InvalidInputsTable.getInvalidInputsTable(invalidInputList)

        return render(request, 'searchResult.html', ret)
