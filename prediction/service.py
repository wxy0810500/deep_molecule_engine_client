from typing import Tuple, List

from prediction.forms import ADMETModelInputForm
from prediction.predictionTask import predictLigand, predictStructure
from smiles.searchService import searchDrugReferenceByInputRequest
import pandas as pd
import os
import numpy as np

DB_FILE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')


def _getCleanedSmilesInfoListFromInputForm(request, inputForm) -> Tuple[List[dict], List[str]]:
    drugRefDF, invalidInputList = searchDrugReferenceByInputRequest(request, inputForm)
    if drugRefDF.size == 0:
        return None, invalidInputList
    return drugRefDF[['input', 'drug_name', 'cleaned_smiles']].to_dict(orient='records'), invalidInputList


def processADMET(request, inputForm: ADMETModelInputForm):
    smilesInfoList, invalidInputList = _getCleanedSmilesInfoListFromInputForm(request, inputForm)
    if smilesInfoList:
        modelTypes = inputForm.cleaned_data['modelTypes']
        preRet = predictLigand(modelTypes, smilesInfoList)
    else:
        preRet = None
    return preRet, invalidInputList
