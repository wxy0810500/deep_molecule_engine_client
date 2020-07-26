from rdkit import Chem, DataStructs
from rdkit.Chem import Draw, AllChem, rdFMCS
from rdkit.Chem.rdchem import Mol
from rdkit import rdBase
rdBase.DisableLog('rdApp.error')
rdBase.DisableLog('rdApp.info')  

import numpy as np
import pandas as pd
from scipy import stats


def read_across_class(df, feature=None, clusters='clusters', read_across_column='read_across'):
    #simple read across based on mode of one feature to map onto other SMILES structures of same cluster
    #reads a numerical value and maps onto same cluster compounds with missing values.

    df[read_across_column] = None
    for cluster in list(df[clusters].unique()):
        if cluster != -1:
            try:
                label = int(stats.mode(df[df[clusters]==cluster][feature])[0])
                df_s1i = df[df[clusters]==cluster].index
                df[read_across_column].loc[df_s1i] = label
            except:
                pass 


    for i in range(0, len(df)):
        if pd.notnull(df[feature].iloc[i]):
            df[read_across_column].iloc[i] = df[feature].iloc[i]
        else:
            df[read_across_column].iloc[i] = df[read_across_label].iloc[i]

    return df

def read_across_label(df, feature=None, clusters='clusters', read_across_column='read_across'):
    #simple read across based on mode of one feature to map onto other SMILES structures of same cluster
    #reads a string feature from another df and maps it onto original dataframe by previous clustering workflow

    df[read_across_column] = 'None'
    df.reset_index(drop=True, inplace=True)
    for cluster in list(df[clusters].unique()):
        if cluster != -1:
            try:
                label = str(stats.mode(df[df[clusters]==cluster][feature])[0][0]) #chooses most common value
                df_s1i = df[df[clusters]==cluster].index
                df[read_across_column].loc[df_s1i] = label
            except:
                pass 


    return df
