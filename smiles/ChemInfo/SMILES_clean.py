from rdkit import Chem, DataStructs
from rdkit.Chem import Draw, AllChem
from rdkit import rdBase
import numpy as np
import pandas as pd
# import modified versions of the 2 python files
from . import HandyFullMolecularProperties as hfmp
from . import HandyMurckoScaffoldCalculation as hmsc

from rdkit.Chem.MolStandardize import rdMolStandardize
from rdkit.Chem.SaltRemover import SaltRemover

import multiprocessing
from joblib import Parallel, delayed

rdBase.DisableLog('rdApp.error')
rdBase.DisableLog('rdApp.info')


def df_smiles_rename_columns(df: pd.DataFrame):
    col_n = []
    for i in range(0, len(df.columns)):
        col_n.append(df.columns[i].replace(' ', '').lower())
    df.columns = col_n
    return df


def NeutralizeReactionsDict1():
    patts = (
        # Imidazoles
        ('[n+;H]', 'n'),
        # Amines
        ('[N+;!H0]', 'N'),
        # Carboxylic acids and alcohols
        ('[$([O-]);!$([O-][#7])]', 'O'),
        # Thiols
        ('[S-;X1]', 'S'),
        # Sulfonamides
        ('[$([N-;X2]S(=O)=O)]', 'N'),
        # Enamines
        ('[$([N-;X2][C,N]=C)]', 'N'),
        # Tetrazoles
        ('[n-]', '[nH]'),
        # Sulfoxides
        ('[$([S-]=O)]', 'S'),
        # Amides
        ('[$([N-]C=O)]', 'N'))

    return [(Chem.MolFromSmarts(x), Chem.MolFromSmiles(y, False)) for x, y in patts]


_reactions = None


def NeutralizeCharges(smiles, reactions=None):
    global _reactions
    if reactions is None:
        if _reactions is None:
            _reactions = NeutralizeReactionsDict1()
        reactions = _reactions
    mol = Chem.MolFromSmiles(smiles)
    replaced = False
    for i, (reactant, product) in enumerate(reactions):
        while mol.HasSubstructMatch(reactant):
            try:
                replaced = True
                rms = AllChem.ReplaceSubstructs(mol, reactant, product)
                mol = rms[0]
            except RuntimeError:
                replaced = False
    if replaced:
        return (Chem.MolToSmiles(mol, True), True)
    else:
        return (smiles, False)


def neutralizeRadicals(mol):
    for a in mol.GetAtoms():
        if a.GetNumRadicalElectrons() == 1 and a.GetFormalCharge() == 1:
            a.SetNumRadicalElectrons(0)
            a.SetFormalCharge(0)
    return mol


def countAtoms(smiles, atom='C'):
    if type(smiles) is str:
        mol = Chem.MolFromSmiles(smiles)
    else:
        mol = smiles

    atom = '[' + atom + ']'
    patt = Chem.MolFromSmarts(atom)
    pm = mol.GetSubstructMatches(patt)
    return len(pm)


def countCarbons(smiles):
    # pass count all atoms function
    return countAtoms(smiles, atom='C')


###################################MAIN FUNCTION####################################################################
####################################################################################################################
####################################################################################################################

def smiles_preprocessing(df: pd.DataFrame, inputfield='SMILES', chiral=True, parallel=False, n_cores=2, remove_duplicates=False,
                         remove_error=False, remove_polymer=True, remove_inorganic=True, fps=True):
    # molecules from SMILES
    # df_compounds = df['SMILES']
    # input df containing smiles column, return same df with canonical smiles, cleaned smiles, scaffolds

    # saltstr="[Na,Ca,K,Mg,Al,Cu,B,Li,Au,Ag,Fe,Zn,Mn,Ni,Br,Cl,I,Gd,Co,Pt,Ti,Ni,Cr]" #old string, replace with sorted str
    remover = SaltRemover(defnData="[Li,Be,B,Na,Mg,Al,Cl,K,Ca,Ti,Cr,Mn,Fe,Co,Ni,Cu,Zn,Ga,Br,Pd,Ag,Sn,I,Pt,Au,Pb]")
    print('start')
    if parallel is True:
        if n_cores == -1:
            n_cores = multiprocessing.cpu_count()
        print(n_cores)
        cores = list(np.linspace(0, n_cores - 1, n_cores).astype(int))
        smiles_n = np.array_split(df, n_cores)

        can_smiles = Parallel(n_jobs=n_cores)(
            delayed(hfmp.transform_smiles)(df_n, inputsmilefield=inputfield, parallel=True, chiral=chiral) for
            core, df_n in zip(cores, smiles_n))
        correct_smiles = df
        correct_smiles['canonical_smiles'] = list(np.concatenate(can_smiles))

        # get iterables for parallel processing
        smiles_n = []
        smiles_n = np.array_split(correct_smiles, n_cores)
        for i in range(0, len(smiles_n)):
            smiles_n[i] = tuple([smiles_n[i], chiral, remove_polymer, remove_inorganic])

        with multiprocessing.Pool(n_cores) as pool:
            correct_smiles = pd.concat(pool.starmap(_process_loop, smiles_n), ignore_index=True)

        # cleaned_smiles = Parallel(n_jobs=-1)(delayed(_process_loop2)(df_n) for core, df_n in zip(cores, smiles_n))
        # correct_smiles['cleaned_smiles'] = list(np.concatenate(cleaned_smiles))

        fps = False
        fps1 = []

    else:
        correct_smiles = hfmp.transform_smiles(df, inputsmilefield=inputfield, chiral=chiral)

        scaffolds = []
        cleaned_smiles = []
        mol_list = []

        for i in range(0, len(correct_smiles)):
            smiles = Chem.MolFromSmiles(correct_smiles['canonical_smiles'].iloc[i])
            cleaned_smile, scaffold, res = _smiles_process(smiles, remover, chiral=chiral,
                                                           remove_polymer=remove_polymer,
                                                           remove_inorganic=remove_inorganic)

            cleaned_smiles.append(cleaned_smile)
            scaffolds.append(scaffold)

            if res is not None:
                mol_list.append(res)
            # else: #debug use only
            # print('None', i)

        correct_smiles['cleaned_smiles'] = cleaned_smiles
        correct_smiles['scaffolds'] = scaffolds

    if fps is True:
        fps1 = [AllChem.GetMorganFingerprintAsBitVect(m, 2) for m in mol_list]
    else:
        fps1 = []

    if remove_duplicates is True:
        correct_smiles = correct_smiles.drop_duplicates(subset='cleaned_smiles')

    if remove_error is True:
        correct_smiles = correct_smiles[correct_smiles['cleaned_smiles'].notna()]

    return correct_smiles, fps1


def smiles_train_test_sets(df, inputcolumn='cleaned_smiles'):
    df = df_smiles_rename_columns(df)
    chiral = list(df['cleaned_smiles'])

    achiral = []
    for smiles in chiral:
        try:
            achiral.append(Chem.MolToSmiles(Chem.MolFromSmiles(smiles), isomericSmiles=False))
        except:
            achiral.append(None)
    df['smiles_cleaned'] = chiral
    df['smiles_achiral'] = achiral

    if 'px' not in list(df.columns):
        df['px'] = None
    if 'label' not in list(df.columns):
        try:
            df['label'] = [1 if x >= 6 else 0 for x in list(df['px'])]
        except:
            df['label'] = None

    return df[['px', 'smiles_cleaned', 'smiles_achiral', 'label']]


####################################################################################################################
####################################################################################################################
####################################################################################################################


def _process_loop(df1, chiral, remove_polymer, remove_inorganic):
    remover = SaltRemover(defnData="[Li,Be,B,Na,Mg,Al,Cl,K,Ca,Ti,Cr,Mn,Fe,Co,Ni,Cu,Zn,Ga,Br,Pd,Ag,Sn,I,Pt,Au,Pb]")
    scaffolds = list(np.zeros(len(df1)))
    cleaned_smiles = list(np.zeros(len(df1)))

    for i in range(0, len(df1)):
        smiles = Chem.MolFromSmiles(df1['canonical_smiles'].iloc[i])
        cleaned_smile, scaffold, _ = _smiles_process(smiles, remover, chiral=chiral,
                                                     remove_polymer=remove_polymer,
                                                     remove_inorganic=remove_inorganic)
        cleaned_smiles[i] = cleaned_smile
        scaffolds[i] = scaffold

    df1['cleaned_smiles'] = cleaned_smiles
    df1['scaffolds'] = scaffolds
    df2 = df1
    return df2


def processOneSmiles(smiles, remover_tool, chiral=True, remove_polymer=True, remove_inorganic=True):
    return _smiles_process(smiles, remover_tool,
                    chiral=chiral, remove_polymer=remove_polymer, remove_inorganic=remove_inorganic)


def _smiles_process(smiles, remover_tool, chiral=True, remove_polymer=True, remove_inorganic=True):
    # input smiles string or RDkit mol object

    # use if remover tool does not load from previous step, otherwise load from higher level due to memory
    if remover_tool is None:
        remover_tool = SaltRemover(
            defnData="[Li,Be,B,Na,Mg,Al,Cl,K,Ca,Ti,Cr,Mn,Fe,Co,Ni,Cu,Zn,Ga,Br,Pd,Ag,Sn,I,Pt,Au,Pb]")

    if type(smiles) is str:
        smiles = Chem.MolFromSmiles(smiles)

    if smiles is not None:
        try:
            try:
                cleaned_mol = rdMolStandardize.Cleanup(smiles)
                res = remover_tool.StripMol(cleaned_mol, dontRemoveEverything=False)
            except:
                print(Chem.MolToSmiles(smiles))
                res = remover_tool.StripMol(smiles, dontRemoveEverything=True)

            try:
                res1 = neutralizeRadicals(res)
            except:
                res1 = res

            smiles_str = NeutralizeCharges(Chem.MolToSmiles(res1), reactions=NeutralizeReactionsDict1())[0]

            try:
                smiles_str = smiles_str.replace('[NH-]', '[NH2]')
            except:
                smiles_str.replace(' ', '')

            if chiral is False:
                smiles_str = smiles_str.replace('@', '').replace('/', '').replace('\\', '')

            # replace/remove wildcard atom
            smiles_str = smiles_str.replace('*', '').replace('()', '')

            if remove_polymer is True:
                sml = smiles_str.find('.')
                if sml != -1:
                    strlist = smiles_str.split('.')
                    strlistidx = [len(x) for x in strlist]
                    smiles_str = strlist[np.argmax(strlistidx)]
                else:
                    smiles_str = smiles_str

            # generate smiles string and figure object
            try:
                _res = Chem.MolFromSmiles(smiles_str)
                _cleaned_smiles = Chem.MolToSmiles(Chem.MolFromSmiles(smiles_str))

            except:
                _res = None
                _cleaned_smiles = None

            # generate scaffolds
            try:
                _scaffolds = hmsc.generate_scaffold(smiles_str)
            except:
                _scaffolds = None

            if remove_inorganic is True:
                if countCarbons(_cleaned_smiles) == 0:
                    _cleaned_smiles = None
                    _res = None
        except:
            _cleaned_smiles = None  # changed from 'error'
            _scaffolds = None  # changed from '""'
            _res = None
    else:
        _cleaned_smiles = None  # changed from 'error'
        _scaffolds = None  # changed from '""'
        _res = None

    # print(_cleaned_smiles)
    return _cleaned_smiles, _scaffolds, _res


def identify_duplicates2(f1, f2, df_field='cleaned_smiles'):
    # modified version of existing identify_duplicates def
    duplist = []
    idxlist = []
    catlist = []

    for i in range(0, len(f1)):
        s1 = f1[df_field].iloc[i]
        if s1 in list(f2[df_field]):
            duplist.append(s1)
            catlist.append(list(f2[df_field]).index(s1))
            # print(s1, i)
            idxlist.append(i)

    FP = pd.DataFrame(duplist)
    return FP, idxlist, catlist


def identify_duplicates3(f1, f2, f3, df_field='none'):
    duplist = []  # smiles
    idxlist = []  # index list of reframe
    catlist = []  # variable index list from smiles list
    idxlist_dups = []  # duplicate indices between fda and reframe

    for i in range(0, len(f1)):
        s1 = f1[df_field].iloc[i]
        if s1 in list(f2[df_field]):
            if s1 not in list(f3[df_field]):
                duplist.append(s1)
                catlist.append(list(f2[df_field]).index(s1))
                # print(s1, i)
                idxlist.append(i)
            else:
                idxlist_dups.append(i)

    FP = pd.DataFrame(duplist)
    return FP, idxlist, catlist, idxlist_dups


def get_scaffold_index(df, scaffold_data=None):
    idxlist = []
    for i in range(0, len(df)):
        s1 = df['scaffolds'].iloc[i]
        idx = scaffold_data[scaffold_data['scaffolds'] == s1].index.values[0]
        if idx in [6816, 6817]:
            idx = 'none'
        idxlist.append(idx)
    df['scaffold_index'] = idxlist
    df1 = df[df['scaffold_index'] != 'none']
    return df1


def get_column_value(df, df2, c, data_field=None):
    df['rankidx'] = c
    if data_field is not None:
        df[data_field] = ""
        for i in range(0, len(df)):
            s1 = df['rankidx'].iloc[i]
            try:
                df[data_field].iloc[i] = df2[data_field].iloc[s1]
            except:
                df[data_field].iloc[i] = None
    df.drop(['rankidx'], axis=1, inplace=True)
    return df


def similarity_matrix(fps):
    fpsL = len(fps)
    M = np.zeros((fpsL, fpsL))
    Mx = []
    for i in range(0, fpsL):
        sims = DataStructs.BulkTanimotoSimilarity(fps[i], fps[:i])
        Mx.extend([x for x in sims])

    M[np.tril_indices(fpsL, k=-1)] = Mx
    M[np.triu_indices(fpsL, k=1)] = Mx
    return M


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-file', type=str, default=None, help='input file')
    parser.add_argument('-input', type=str, default='SMILES', help='input file column with SMILES')
    parser.add_argument('-d', type=str, default='False', help='Drop duplicates')
    parser.add_argument('-p', type=str, default='True', help='Remove polymers, keep largest sequence')
    parser.add_argument('-c', type=str, default='True', help='Keep chirality')
    parser.add_argument('-e', type=str, default='False', help='Remove errors')
    parser.add_argument('-i', type=str, default='True', help='Remove inorganic only sequences')
    parser.add_argument('-parallel', type=str, default='False', help='Parallel processing')

    args = parser.parse_args()

    dffile = args.file
    inputfield = args.input

    # translate string args to python bool
    if args.d == 'True':
        argsd = True
    else:
        argsd = False

    if args.p == 'True':
        argsp = True
    else:
        argsp = False

    if args.c == 'True':
        argsc = True
    else:
        argsc = False

    if args.e == 'True':
        argse = True
    else:
        argse = False

    if args.parallel == 'True':
        argsp1 = True
    else:
        argsp1 = False

    if args.i == 'True':
        argsi1 = True
    else:
        argsi1 = False

    # print(argsc) #debug code, will be cleaned in the future
    # print(type(argsc))

    try:
        df = pd.read_csv(dffile)
        filen = dffile[:-4]
    except:
        df = pd.read_excel(dffile)
        filen = dffile[:-5]

    df, _ = smiles_preprocessing(df, inputfield=inputfield, fps=False, chiral=argsc, remove_duplicates=argsd,
                                 remove_error=argse, remove_polymer=argsp, parallel=argsp1, n_cores=-1,
                                 remove_inorganic=argsi1)
    df.to_csv(filen + '_cleaned.csv', index=False)
    print('Done')
