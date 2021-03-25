import os
import pandas as pd
from typing import List
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import time

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


def searchDrugReferenceExactlyByName(nameList: List):
    """

    @param nameList:
    @return: [drug_name,smiles,canonical_smiles,cleaned_smiles,scaffolds]
            if there is no result, retDF.size == 0
    """
    isInList = DRUG_REFERENCE_DB_DRUG_NAME_LOWER_SERIES.isin(nameList)
    retDF = DRUG_REFERENCE_DB_DF[isInList]

    return retDF


def searchDrugReferenceFuzzilyByName(nameList: List):
    """

    @param nameList:
    @return:

    """

    # retList = []
    # for queryName in nameList:
    #     ret = process.extractOne(queryName, DRUG_REFERENCE_DB_DRUG_NAME_LOWER_SERIES)
    #     retList.append(ret)
    return pd.DataFrame(([queryName, drugName, cleanedSmiles, scaffolds]
                         for drugName, cleanedSmiles, scaffolds in
                         zip(DRUG_REFERENCE_DB_DF['drug_name'], DRUG_REFERENCE_DB_DF['cleaned_smiles'],
                             DRUG_REFERENCE_DB_DF['scaffolds']) for queryName in set(nameList) if
                         queryName.lower() in drugName.lower()),
                        columns=['input', 'drug_name', 'cleaned_smiles', 'scaffolds'])


def searchDrugReferenceFuzzilyByName_df_contains(nameList: List):
    retDF = pd.DataFrame()
    for queryName in nameList:
        mask = DRUG_REFERENCE_DB_DRUG_NAME_LOWER_SERIES.str.contains(queryName.lower())
        searchDF = DRUG_REFERENCE_DB_DF[mask]
        # searchDF['input'] = queryName
        retDF.append(searchDF)

    return retDF


def searchDrugReferenceFuzzilyByName_df_itertuple(nameList: List):
    return [{queryName: [row
                         for row in
                         DRUG_REFERENCE_DB_DF.itertuples()
                         if queryName.lower() in row.drug_name.lower()]} for queryName in nameList]


# if __name__ == '__main__':
#     inputList = ["colestipol"]
#     time_start = time.time()
#     df = searchDrugReferenceFuzzilyByName(inputList)
#     time_end = time.time()
#     print('totally cost', time_end - time_start)
#     # print(df)
    # time_start = time.time()
    # df = searchDrugReferenceFuzzilyByName_df_itertuple(inputList)
    # time_end = time.time()
    # print('totally cost', time_end - time_start)
    #
    # time_start = time.time()
    # df = searchDrugReferenceFuzzilyByName_df_contains(inputList)
    # time_end = time.time()
    # print('totally cost', time_end - time_start)
    #
    # time_start = time.time()
    # searchDrugReferenceExactlyByName(inputList)
    # time_end = time.time()
    # print('totally cost', time_end - time_start)
    print('-------------------------')
