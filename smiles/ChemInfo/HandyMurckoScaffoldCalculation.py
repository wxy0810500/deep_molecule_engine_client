import pandas as pd
from rdkit import Chem
import numpy as np
from rdkit.Chem.Scaffolds import MurckoScaffold


def generate_scaffold(smiles, include_chirality=False):
    """Compute the Bemis-Murcko scaffold for a SMILES string."""
    scaffold = MurckoScaffold.MurckoScaffoldSmilesFromSmiles(
        smiles, includeChirality=include_chirality)
    return scaffold


def ScaffolderDiversity(input_file, smile_field, output_file, save_csv=False):
    if input_file is type(str):
        input = pd.read_csv(input_file)
    else:
        input = input_file
    input1 = input[input['Value'] == 0]
    input2 = input[input['Value'] == 1]
    correct_smiles = []
    for i in input1[smile_field]:
        try:
            correct_smiles.append(Chem.MolToSmiles(Chem.MolFromSmiles(i)))
        except:
            correct_smiles.append(i)

    correct_smiles = set(correct_smiles)

    scaffoldList = []
    for i in correct_smiles:
        try:
            scaffold = generate_scaffold(i, include_chirality=True)
        except:
            scaffold = 'NA'
        if scaffold == '':
            scaffold = 'NA'
        scaffoldList.append(scaffold)
    scaffoldList.remove('NA')
    unique = set(scaffoldList)
    ScaffoldDF1 = pd.DataFrame(list(unique), columns=['smiles'])
    ScaffoldDF1['label'] = 0
    correct_smiles = []
    for i in input2[smile_field]:
        try:
            correct_smiles.append(Chem.MolToSmiles(Chem.MolFromSmiles(i)))
        except:
            correct_smiles.append(i)

    correct_smiles = set(correct_smiles)

    scaffoldList = []
    for i in correct_smiles:
        try:
            scaffold = generate_scaffold(i, include_chirality=True)
        except:
            scaffold = 'NA'
        if scaffold == '':
            scaffold = 'NA'
        scaffoldList.append(scaffold)
    scaffoldList.remove('NA')
    unique = set(scaffoldList)
    ScaffoldDF2 = pd.DataFrame(list(unique), columns=['smiles'])
    ScaffoldDF2['label'] = 1
    ScaffoldDF = pd.concat([ScaffoldDF1, ScaffoldDF2])
    if save_csv is True:
        ScaffoldDF.dropna().to_csv(output_file, index=False, encoding='utf8')
    ScaffolderDiversity = float(ScaffoldDF.shape[0]) / float(len(correct_smiles))
    print("Total Number of Scaffolds is {}".format(ScaffoldDF.shape[0]))
    print("Total Number of Compounds is {}".format((input.shape[0])))
    print("Scaffold Diversity (From 0 to 1) is {}".format(round(ScaffolderDiversity, 3)))
    return ScaffoldDF.dropna()


def GenerateMolPerScaffold(input_file, smile_field, output_file, output_all, save_csv=False):
    input = pd.read_csv(input_file)
    correct_smiles = []
    for i in input[smile_field]:
        try:
            correct_smiles.append(Chem.MolToSmiles(Chem.MolFromSmiles(i)))
        except:
            correct_smiles.append(i)

    correct_smiles = set(correct_smiles)

    scaffoldlist = []
    for i in correct_smiles:
        try:
            scaffold = generate_scaffold(i, include_chirality=True)
        except:
            scaffold = 'NA'
        if scaffold == '':
            scaffold = 'NA'
        scaffoldlist.append(scaffold)

    input['scaffold_smiles'] = scaffoldlist
    input.to_csv(output_all)

    output = input.groupby(['scaffold_smiles']).first()  ##### get the first molecule of each scaffold
    print(output.head(10))

    if save_csv is True:
        output.to_csv(output_file)

    return outfile_file

##### change input according the purpose#####################

# ScaffolderDiversity("../../Dataset/TB_Ekins/TB_2017_100nM.csv", 'SMILES','../../Dataset/TB_Ekins/TB_100nM_Testing_scaffold.csv')

# GenerateMolPerScaffold("../../Dataset/TB_Ekins/TB_full_consolidate_Threshold_1uM_plus_invivo.csv", 'SMILES', '../../Dataset/TB_Ekins/TB_full_consolidate_Threshold_1uM_plus_invivo_unique_scaffold_active.csv','../../Dataset/TB_Ekins/TB_full_consolidate_Threshold_1uM_plus_invivo_withscaffold_active.csv')
