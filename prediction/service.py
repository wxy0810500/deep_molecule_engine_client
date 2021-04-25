from typing import Tuple, List

from prediction.forms import LigandModelInputForm, NetworkModelInputForm
from prediction.predictionTask import predictLigand
from smiles.searchService import searchDrugReferenceByInputRequest
import pandas as pd
import os
import numpy as np

DB_FILE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')


def __getCleanedSmilesInfoListFromInputForm(request, inputForm) -> Tuple[List[dict], List[str]]:
    drugRefDF, invalidInputList = searchDrugReferenceByInputRequest(request, inputForm)
    if drugRefDF.size == 0:
        return None, invalidInputList
    return drugRefDF[['input', 'drug_name', 'cleaned_smiles']].to_dict(orient='records'), invalidInputList


def processLigand(request, inputForm: LigandModelInputForm):
    smilesInfoList, invalidInputList = __getCleanedSmilesInfoListFromInputForm(request, inputForm)
    if smilesInfoList:
        modelTypes = inputForm.cleaned_data['modelTypes']
        preRetList = predictLigand(modelTypes, smilesInfoList)
    else:
        preRetList = None
    return preRetList, invalidInputList


NETWORK_TRAINING_RESULT_DF: pd.DataFrame = pd.read_csv(os.path.join(DB_FILE_BASE_DIR,
                                                       'training_viral_network_final_result.csv'),
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
    searchRetDF: pd.DataFrame = cleanedSmilesDF.merge(NETWORK_TRAINING_RESULT_DF, on='cleaned_smiles', how='left')
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
    rawDF.fillna('', inplace=True)
    return predictRetDF, rawDF, invalidInputList





