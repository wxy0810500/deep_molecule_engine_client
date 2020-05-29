from django.shortcuts import render
from django.http import HttpResponse
from deep_engine_client.forms import TextInputForm
from deep_engine_client.sysConfig import *
from smiles.cleanSmiles import cleanSmilesListSimply
from smiles.searchService import searchDrugReferenceByCleanedSmiles
from .service import *
from .tables import SearchResultTable
import pandas as pd

# Create your views here.
INPUT_TEMPLATE_FORMS = {
    SERVICE_TYPE_SEARCH: {
        'inputForm': TextInputForm(),
        'actionURL': SERVICE_TYPE_SEARCH,
        'statement': "We have curated over 7000 antiviral compounds and respective virus species available "
                     "for search based on in vitro viral infection assay results (EC50<=1uM) and in vivo results"
    }
}


def searchIndex(request):
    return render(request, 'input.html', INPUT_TEMPLATE_FORMS.get(SERVICE_TYPE_SEARCH))


def advancedSearch(request):
    if request.method != 'POST':
        return HttpResponse('invalid http method')

    inputForm = TextInputForm(request.POST)
    inputType = inputForm.cleaned_data['inputType']
    inputStr = inputForm.cleaned_data['inputStr']

    if TextInputForm.INPUT_TYPE_DRUG_NAME == inputType:
        inputDrugNameList = TextInputForm.filterInputDrugNames(inputStr)
        searchDrugReferenceExactByName(inputDrugNameList)
    else:
        # smiles
        inputSmilesList = TextInputForm.filterInputSmiles(inputStr)
        # clean smiles
        cleanedSmiles: list[tuple] = cleanSmilesListSimply(inputSmilesList)
        csDF = pd.DataFrame(data=cleanedSmiles, columns=['input', 'cleaned_smiles', 'scaffolds'])
        # query drug name
        drugRefDF = searchDrugReferenceByCleanedSmiles(csDF)

    # filter scaffolds in blacklist
    validDrugRetDF = filterScaffoldInBlacklist(drugRefDF)

    # query virus info
    csRetDF = searchBroadSpectrumAntiviralDataByCleanedSmiles(validDrugRetDF)
    scaffoldsRetDF = searchBroadSpectrumAntiviralDataByScaffolds(validDrugRetDF)

    ret = {
        "exactMapTable": SearchResultTable(csRetDF.to_dict(orient='record')),
        "scaffoldMapTable": SearchResultTable(scaffoldsRetDF.to_dict(orient='record'))
    }

    return render(request, 'searchResult.html', ret)
