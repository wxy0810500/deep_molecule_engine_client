import os
import pandas as pd

DB_FILE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')
BROAD_SPECTRUM_ANTIVIRAL_DB_DF: pd.DataFrame = pd.read_csv(os.path.join(DB_FILE_BASE_DIR,
                                                                        'broad_spectrum_antiviral.csv'))
SCAFFOLDS_BLACKLIST = pd.read_csv(os.path.join(DB_FILE_BASE_DIR, 'scaffold_blacklist.csv'))['scaffolds'].tolist()


def filterScaffoldInBlacklist(dfWithScaffolds: pd.DataFrame):
    return dfWithScaffolds[~dfWithScaffolds['scaffolds'].isin(SCAFFOLDS_BLACKLIST)]


def searchBroadSpectrumAntiviralDataByCleanedSmiles(dfWithCleanedSmiles: pd.DataFrame) -> pd.DataFrame:
    ret = pd.merge(dfWithCleanedSmiles, BROAD_SPECTRUM_ANTIVIRAL_DB_DF[~'scaffolds'],
                   on='cleaned_smiles', how='left')
    print(f'cSmiles-virus\n{ret.to_dict()}')
    return ret


def searchBroadSpectrumAntiviralDataByScaffolds(dfWithScaffolds: pd.DataFrame):
    ret = pd.merge(dfWithScaffolds, BROAD_SPECTRUM_ANTIVIRAL_DB_DF[~'cleaned_smiles'],
                   on='scaffolds', how='left')
    print(f'scaffolds-virus\n{ret.to_dict()}')
    return ret
