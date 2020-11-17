from typing import Tuple, List

from prediction.forms import StructureModelInputForm
from smiles.searchService import searchDrugReferenceByInputRequest
import os
from utils.fileUtils import handleUploadedFile
from prediction.predictionTask import predictSBVS

DB_FILE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')


def _getCleanedSmilesInfoListFromInputForm(request, inputForm) -> Tuple[List[dict], List[str]]:
    drugRefDF, invalidInputList = searchDrugReferenceByInputRequest(request, inputForm)
    if drugRefDF.size == 0:
        return None, invalidInputList
    return drugRefDF[['input', 'drug_name', 'cleaned_smiles']].to_dict(orient='records'), invalidInputList


def processSBVS(request, inputForm: StructureModelInputForm):
    smilesInfoList, invalidInputList = _getCleanedSmilesInfoListFromInputForm(request, inputForm)
    if smilesInfoList:
        # get pdbFile
        pdbContent = handleUploadedFile(request.FILES['uploadPDBFile'])

        modelTypes = inputForm.cleaned_data['modelTypes']
        preRetList, allSmilesDict = predictSBVS(modelTypes, smilesInfoList, pdbContent)
    else:
        preRetList = None
    return preRetList, invalidInputList

