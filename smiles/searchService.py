import pandas as pd
import os
from deep_engine_client.forms import TextInputForm
from .cleanSmiles import cleanSmilesListSimply
from typing import Union, List

DB_FILE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')
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


def searchDrugReferenceExactlyByName(nameList: List):
    isInList = DRUG_REFERENCE_DB_DRUG_NAME_LOWER_SERIES.isin(nameList)
    retDF = DRUG_REFERENCE_DB_DF[isInList]
    if retDF.size == 0:
        retDF = None
    return retDF


def searchDrugReferenceByTextInputData(inputType: str, inputStr: str) -> Union[None, pd.DataFrame]:
    if TextInputForm.INPUT_TYPE_DRUG_NAME == inputType:
        inputDrugNameList = TextInputForm.filterInputDrugNames(inputStr)

        drugRefDF = searchDrugReferenceExactlyByName(inputDrugNameList)
        # 加入input 列
        drugRefDF['input'] = drugRefDF['drug_name']
    else:
        # smiles
        inputSmilesList = TextInputForm.filterInputSmiles(inputStr)
        # clean smiles
        cleanedSmiles: List[tuple] = cleanSmilesListSimply(inputSmilesList)
        # clean entries without cleaned smiles
        cleanedSmiles = [entry for entry in cleanedSmiles if entry[1] is not None]
        csDF = pd.DataFrame(data=cleanedSmiles, columns=['input', 'cleaned_smiles', 'scaffolds'])

        # query drug name
        drugRefDF = searchDrugReferenceByCleanedSmiles(csDF)
        # 
    if drugRefDF.size == 0:
        drugRefDF = None
    return drugRefDF

#
# df = pd.read_csv(‘tox21_sample.csv')
# dme = pd.read_csv('drug_reference.csv') #table2
#
# #cleaned smiles
# dme_lookup = pd.merge(df, dme[['drug_name', 'DrugBank ID', 'CID', 'cleaned_smiles']], on='cleaned_smiles', how='inner')
#
# #Scaffolds
# dme_lookup_sc = pd.merge(df[df['scaffolds'].notna()], dme[['drug_name', 'DrugBank ID', 'CID', 'scaffolds']], on='scaffolds', how='inner')
#
# #name lookup
# df = pd.read_csv('dme_db_example.csv') #新的表
# df['drug_name'] = df['drug_name'].str.lower()
# #if individual string: str1 = str1.lower()
#
# dme['drug_name'] = dme['drug_name'].str.lower()
#
# _, i1, c1 = identify_duplicates2(df, dme, df_field='drug_name')
# df_dme = df.iloc[i1, :]
# colname = ['cleaned_smiles', 'scaffolds', 'DrugBank ID', 'CID']
# for column in colname:
#     df_dme = get_column_value(df_dme, dme, c1, data_field=column) #final table for smiles and scaffolds advancedSearch
