from deep_engine_client.forms import TextInputForm
from smiles.cleanSmiles import cleanSmilesListSimply
from smiles.searchService import *
from typing import Tuple, List
from django.http import Http404

DB_FILE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')
BROAD_SPECTRUM_ANTIVIRAL_DB_DF: pd.DataFrame = pd.read_csv(os.path.join(DB_FILE_BASE_DIR,
                                                                        'broad_spectrum_antiviral.csv'))
BROAD_SPECTRUM_ANTIVIRAL_DB_WITHOUT_SCAFFOLDS_DF: pd.DataFrame = \
    BROAD_SPECTRUM_ANTIVIRAL_DB_DF.drop(['scaffolds', 'drug_name'], axis=1)
BROAD_SPECTRUM_ANTIVIRAL_DB_WITHOUT_CLEANED_SMILES_DF: pd.DataFrame = \
    BROAD_SPECTRUM_ANTIVIRAL_DB_DF.drop(['cleaned_smiles', 'drug_name'], axis=1)

SCAFFOLDS_BLACKLIST = pd.read_csv(os.path.join(DB_FILE_BASE_DIR, 'scaffold_blacklist.csv'))['scaffolds'].tolist()


def filterScaffoldInBlacklist(dfWithScaffolds: pd.DataFrame):
    return dfWithScaffolds[~dfWithScaffolds['scaffolds'].isin(SCAFFOLDS_BLACKLIST)]


def searchBroadSpectrumAntiviralDataByCleanedSmiles(dfWithCleanedSmiles: pd.DataFrame) -> pd.DataFrame:
    ret = pd.merge(dfWithCleanedSmiles, BROAD_SPECTRUM_ANTIVIRAL_DB_WITHOUT_SCAFFOLDS_DF,
                   on='cleaned_smiles', how='left')
    ret.fillna('', inplace=True)
    # print(f'cSmiles-virus\n{ret.to_dict()}')
    return ret


def searchBroadSpectrumAntiviralDataByScaffolds(dfWithScaffolds: pd.DataFrame):
    ret = pd.merge(dfWithScaffolds, BROAD_SPECTRUM_ANTIVIRAL_DB_WITHOUT_CLEANED_SMILES_DF,
                   on='scaffolds', how='left')
    ret.fillna('', inplace=True)
    # print(f'scaffolds-virus\n{ret.to_dict()}')
    return ret


def doAdvancedSearch(inputType: str, inputStr: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    drugRefDF = searchDrugReferenceByTextInputData(inputType, inputStr)

    if drugRefDF is None:
        raise Http404()

    # filter scaffolds in blacklist
    validDrugRetDF = filterScaffoldInBlacklist(drugRefDF)

    # query virus info
    csRetDF = searchBroadSpectrumAntiviralDataByCleanedSmiles(validDrugRetDF)
    scaffoldsRetDF = searchBroadSpectrumAntiviralDataByScaffolds(validDrugRetDF)
    return csRetDF, scaffoldsRetDF
