from typing import Tuple, List

from prediction.forms import TFModelInputForm
from prediction.predictionTask import predictTF
from smiles.searchService import searchDrugReferenceByInputRequest
import os

DB_FILE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')


def _getCleanedSmilesInfoListFromInputForm(request, inputForm) -> Tuple[List[dict], List[str]]:
    drugRefDF, invalidInputList = searchDrugReferenceByInputRequest(request, inputForm)
    if drugRefDF.size == 0:
        return None, invalidInputList
    return drugRefDF[['input', 'drug_name', 'cleaned_smiles']].to_dict(orient='records'), invalidInputList


def processTF(request, inputForm: TFModelInputForm):
    smilesInfoList, invalidInputList = _getCleanedSmilesInfoListFromInputForm(request, inputForm)
    if smilesInfoList:
        inputCategorys = inputForm.cleaned_data['categorys']
        preRet, smilesDict = predictTF(inputCategorys, smilesInfoList)
    else:
        inputCategorys, smilesDict, preRet = None, None, None
    return preRet, invalidInputList, inputCategorys, smilesDict
