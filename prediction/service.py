from typing import Tuple, List

from prediction.forms import LigandModelInputForm, StructureModelInputForm, NetworkModelInputForm
from prediction.predictionTask import predictLigand, predictStructure
from smiles.searchService import searchDrugReferenceByInputRequest
from utils.fileUtils import handleUploadedFile, handleUploadedExcelFile
import pandas as pd
import os
import numpy as np

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


NETWORK_RESULT_DF: pd.DataFrame = pd.read_csv(os.path.join(DB_FILE_BASE_DIR, 'training_viral_network_final_result.csv'),
                                              float_precision='high')


def processNetWork(request, inputForm: NetworkModelInputForm):
    # get smiles
    drugRefDF, invalidInputList = searchDrugReferenceByInputRequest(request, inputForm)

    if drugRefDF.size == 0:
        return None, None, invalidInputList

    # search result in networkResultDF on cleaned smiles
    drugRefDF = drugRefDF.loc[:, ['input', 'drug_name', 'cleaned_smiles']]
    drugRefDF.reset_index(drop=True, inplace=True)
    cleanedSmilesDF = drugRefDF.loc[:, ['input', 'cleaned_smiles']]
    searchRetDF: pd.DataFrame = cleanedSmilesDF.merge(NETWORK_RESULT_DF, on='cleaned_smiles', how='left')
    numberRetDF: pd.DataFrame = searchRetDF[searchRetDF.columns[3:]]
    # filter raw result: float number > 10
    predictRetDF = numberRetDF.applymap(lambda x: x if float(x) < 10.0 else np.nan)

    rawDF = numberRetDF.applymap(lambda x: x - 10.0 if float(x) > 1.0 else np.nan)

    predictRetDF = drugRefDF.merge(predictRetDF, right_index=True, left_index=True)
    rawDF = drugRefDF.merge(rawDF, right_index=True, left_index=True)

    # print(predictRetDF)
    # print(rawDF)
    predictRetDF.fillna('', inplace=True)
    rawDF.dropna(axis=1, how='all', inplace=True)
    return predictRetDF, rawDF, invalidInputList





