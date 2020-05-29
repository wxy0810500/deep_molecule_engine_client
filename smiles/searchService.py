import pandas as pd
import os


DB_FILE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'smiles\\db')
DRUG_REFERENCE_DB_DF: pd.DataFrame = pd.read_csv(os.path.join(DB_FILE_BASE_DIR, 'drug_reference.csv'))


def searchDrugReferenceByCleanedSmiles(dfWithCleanedSmiles: pd.DataFrame) -> pd.DataFrame:
    return pd.merge(dfWithCleanedSmiles, DRUG_REFERENCE_DB_DF[['drug_name', 'cleaned_smiles']],
                    on='cleaned_smiles', how='inner')


def searchDrugReferenceExactByName(nameList: list):
    pass


def queryDrugReferenceByDrugName(dfWithDrugName: pd.DataFrame):
    retDF = pd.merge(dfWithDrugName, DRUG_REFERENCE_DB_DF[['drug_name', 'cleaned_smiles', 'scaffolds']],
                     on='drug_name', how='inner')
    retDF.drop_duplicates(subset=['drug_name'], inplace=True)
    return retDF


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
