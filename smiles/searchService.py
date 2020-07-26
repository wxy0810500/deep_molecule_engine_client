import pandas as pd
import os
from deep_engine_client.forms import TextInputForm
from .cleanSmiles import cleanSmilesListSimply
from typing import Union, List, Tuple
import numpy as np

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
    if ret.size == 0:
        ret = None
    return ret


def searchDrugReferenceExactlyByName(nameList: List):
    """

    @param nameList:
    @return: [drug_name,smiles,canonical_smiles,cleaned_smiles,scaffolds]
    """
    isInList = DRUG_REFERENCE_DB_DRUG_NAME_LOWER_SERIES.isin(nameList)
    retDF = DRUG_REFERENCE_DB_DF[isInList]

    return retDF


def searchDrugReferenceByTextInputData(inputType: str, inputStr: str) -> Tuple[bool, pd.DataFrame]:
    """

    @param inputType:
    @param inputStr:
    @return: ret , drugRefDF [drug_name,smiles,canonical_smiles,cleaned_smiles,scaffolds]
            若未查询到对应的smiles信息，则ret为true
    """
    if TextInputForm.INPUT_TYPE_DRUG_NAME == inputType:
        inputDrugNameList = TextInputForm.filterInputDrugNames(inputStr)

        drugRefDF: pd.DataFrame = searchDrugReferenceExactlyByName(inputDrugNameList)
        # 加入input 列
        if drugRefDF.size != 0:
            drugRefDF['input'] = drugRefDF['drug_name']
            ret = True
        else:
            # 未查到对应的smiles
            pass
    else:
        # smiles
        inputSmilesList = TextInputForm.filterInputSmiles(inputStr)
        # clean smiles
        cleanedSmiles: List[tuple] = cleanSmilesListSimply(inputSmilesList)

        # clean entries without cleaned smiles
        cleanedSmiles = [entry for entry in cleanedSmiles if entry[1] is not None]
        if len(cleanedSmiles) > 0:
            csDF = pd.DataFrame(data=cleanedSmiles, columns=['input', 'cleaned_smiles', 'scaffolds'])

            # query drug name
            drugRefDF = searchDrugReferenceByCleanedSmiles(csDF)
            if drugRefDF is None:
                drugRefDF = csDF
                drugRefDF['drug_name'] = np.nan
        else:
            drugRefDF = None
    return drugRefDF
