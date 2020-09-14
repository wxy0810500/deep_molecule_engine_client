from typing import Tuple, List

from prediction.forms import LigandModelInputForm, StructureModelInputForm, NetworkModelInputForm
from prediction.predictionTask import predictLigand, predictStructure
from smiles.searchService import searchDrugReferenceByInputRequest
from utils.fileUtils import handleUploadedFile, handleUploadedExcelFile
import pandas as pd
import os

DB_FILE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')


def _getCleanedSmilesInfoListFromInputForm(request, inputForm) -> Tuple[List[dict], List[str]]:
    drugRefDF, invalidInputList = searchDrugReferenceByInputRequest(request, inputForm)
    if drugRefDF.size == 0:
        return None, invalidInputList
    return drugRefDF[['input', 'drug_name', 'cleaned_smiles']].to_dict(orient='records'), invalidInputList


def processLigand(request, inputForm: LigandModelInputForm):
    smilesInfoList, invalidInputList = _getCleanedSmilesInfoListFromInputForm(request, inputForm)
    if smilesInfoList:
        modelTypes = inputForm.cleaned_data['modelTypes']
        preRet = predictLigand(modelTypes, smilesInfoList)
    else:
        preRet = None
    return preRet, invalidInputList


def processStructure(request, inputForm: StructureModelInputForm):
    # get smiles
    smilesInfoList, invalidInputList = _getCleanedSmilesInfoListFromInputForm(request, inputForm)
    if smilesInfoList:
        # get pdbFile
        pdbContent = handleUploadedFile(request.FILES['uploadPDBFile'])

        modelTypes = inputForm.cleaned_data['modelTypes']
        preRet = predictStructure(modelTypes, smilesInfoList, pdbContent)
    else:
        preRet = None
    return preRet, invalidInputList


def initNetworkDB() -> pd.DataFrame:
    rawResultDF: pd.DataFrame = pd.read_csv(
        os.path.join(DB_FILE_BASE_DIR, 'training_viral_network_all_raw.csv'),
    )

    predictResultDF: pd.DataFrame = pd.read_csv(
        os.path.join(DB_FILE_BASE_DIR, 'training_viral_network_all.csv')
    )

    rawResultDF
    return None


NetworkResultDF: pd.DataFrame = initNetworkDB()


def processNetWork(request, inputForm: NetworkModelInputForm):
    # get smiles
    inputType = inputForm.cleaned_data['inputType']
    inputStr = inputForm.cleaned_data['inputStr']
    if request.FILES and request.FILES.get('uploadInputFile', None):
        fileInputList = handleUploadedExcelFile(request.FILES['uploadInputFile'])
    else:
        fileInputList = None






