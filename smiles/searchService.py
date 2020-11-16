import pandas as pd
import os
from deep_engine_client.forms import CommonInputForm
from .cleanSmiles import cleanSmilesListSimply
from typing import List, Tuple, Set
import numpy as np
from utils.fileUtils import getInputDataSetFromUploadedExcel
from deep_engine_client.exception import CommonException

DB_FILE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')
# [drug_name,DrugBank ID,CID,smiles,canonical_smiles,cleaned_smiles,scaffolds]
DRUG_REFERENCE_DB_DF: pd.DataFrame = pd.read_csv(os.path.join(DB_FILE_BASE_DIR, 'drug_reference.csv'))
DRUG_REFERENCE_DB_DRUG_NAME_LOWER_SERIES: pd.Series = DRUG_REFERENCE_DB_DF['drug_name'].str.lower()
DRUG_REFERENCE_WITH_NAME_AND_SMILES: pd.DataFrame = DRUG_REFERENCE_DB_DF[['drug_name', 'cleaned_smiles']]


def searchDrugReferenceByCleanedSmiles(dfWithCleanedSmiles: pd.DataFrame) -> pd.DataFrame:
    searchRet = pd.merge(dfWithCleanedSmiles, DRUG_REFERENCE_WITH_NAME_AND_SMILES, on='cleaned_smiles', how='left')
    searchRet.fillna('', inplace=True)
    ret = searchRet.groupby('input').agg({'drug_name': lambda x: ','.join(x),
                                          'scaffolds': 'first',
                                          'cleaned_smiles': 'first'}).reset_index()
    return ret


def searchDrugReferenceExactlyByName(nameList: List or Set):
    """

    @param nameList:
    @return: [drug_name,smiles,canonical_smiles,cleaned_smiles,scaffolds]
            if there is no result, retDF.size == 0
    """
    isInList = DRUG_REFERENCE_DB_DRUG_NAME_LOWER_SERIES.isin(nameList)
    retDF = DRUG_REFERENCE_DB_DF[isInList]

    return retDF


def searchDrugReferenceByInputRequest(request, inputForm: CommonInputForm) -> Tuple[pd.DataFrame, List[str]]:
    """

    @return: drugRefDF [drug_name,smiles,canonical_smiles,cleaned_smiles,scaffolds], invalidInputList
    """
    inputType = inputForm.cleaned_data['inputType']
    inputStr = inputForm.cleaned_data['inputStr']
    if request.FILES and request.FILES.get('uploadInputFile', None):
        fileInputSet = getInputDataSetFromUploadedExcel(request.FILES['uploadInputFile'])
    else:
        fileInputSet = None

    invalidInputList = None
    if CommonInputForm.INPUT_TYPE_DRUG_NAME == inputType:
        if inputStr:
            inputDrugNameList: List = CommonInputForm.splitAndFilterInputDrugNamesStr(inputStr)
            if fileInputSet is not None:
                inputDrugNameList.extend(fileInputSet)
        else:
            if fileInputSet is not None:
                inputDrugNameList = fileInputSet
            else:
                raise CommonException("both input string and file are empty")
        drugRefDF: pd.DataFrame = searchDrugReferenceExactlyByName(inputDrugNameList)
        if len(inputDrugNameList) == drugRefDF.size:
            # 完全匹配，加入input 列
            drugRefDF.loc[:, 'input'] = drugRefDF['drug_name']
        else:
            if drugRefDF.size != 0:
                # 部分匹配，加入input列
                drugRefDF.loc[:, 'input'] = drugRefDF['drug_name']
            # 未查到对应的smiles
            validList = drugRefDF['drug_name'].to_list()
            invalidInputList = [dName for dName in inputDrugNameList if dName not in validList]
    else:
        if inputStr:
            inputSmilesList: List = CommonInputForm.splitAndFilterInputSmiles(inputStr)
            if fileInputSet is not None:
                inputSmilesList.extend(fileInputSet)
        else:
            if fileInputSet is not None:
                inputSmilesList = fileInputSet
            else:
                raise CommonException("both input string and file are empty")

        # clean smiles
        cleanedSmiles: List[tuple] = cleanSmilesListSimply(inputSmilesList)

        # clean entries without cleaned smiles
        invalidInputList = [entry[0] for entry in cleanedSmiles if entry[1] is None]
        cleanedSmiles = [entry for entry in cleanedSmiles if entry[1] is not None]
        if len(cleanedSmiles) > 0:
            csDF = pd.DataFrame(data=cleanedSmiles, columns=['input', 'cleaned_smiles', 'scaffolds'])

            # query drug name
            drugRefDF = searchDrugReferenceByCleanedSmiles(csDF)
            if drugRefDF.size == 0:
                drugRefDF = csDF
                drugRefDF['drug_name'] = np.nan
        else:
            drugRefDF = pd.DataFrame()
    return drugRefDF, invalidInputList
