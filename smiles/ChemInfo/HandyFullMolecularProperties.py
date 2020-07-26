from rdkit import Chem


#####this script is to generate full molecular properties from known smiles dataset#############


def transform_smiles(inputdata, inputsmilefield='SMILES', save_csv=False, parallel=False, chiral=True):
    #inputdata is df
    correct_smiles=[]
    for i in inputdata[inputsmilefield]:
        try:
            correct_smiles.append(Chem.MolToSmiles(Chem.MolFromSmiles(i), isomericSmiles=chiral))
        except:
            correct_smiles.append('error')

    inputdata['canonical_smiles'] = correct_smiles

    if save_csv is True:
        inputdata.to_csv(index=False)
    
    if parallel is True:
        inputdata1 = list(inputdata['canonical_smiles'])
    else:
        inputdata1 = inputdata
    
    return inputdata1


def get_inchikey(inputdata, inputfield='cleaned_smiles'):
        
    inchilist = []
    for smiles in list(inputdata[inputfield]):
        try:
            inchilist.append(Chem.inchi.MolToInchiKey(Chem.MolFromSmiles(smiles)))
        except:
            inchilist.append(None)
    
    inputdata['inchikey'] = inchilist
    return inputdata


def get_molecular_properties(inputdata, inputfield='cleaned_smiles'):
    properties = [i for i in Chem.rdMolDescriptors.Properties().GetPropertyNames()]
    #print(properties)

    for index, i in enumerate(properties):
        list1 = []
        for j in inputdata[inputfield]:
            try:
                mol = Chem.MolFromSmiles(j)
                list1.append(Chem.rdMolDescriptors.Properties().ComputeProperties(mol)[index])
            except:
                list1.append('error')
        inputdata[i]=list1
    return inputdata
