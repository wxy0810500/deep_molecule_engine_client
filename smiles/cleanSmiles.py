from rdkit.Chem.SaltRemover import SaltRemover
from .ChemInfo.SMILES_clean import processOneSmiles

_DEFAULT_REMOVER_TOOL = SaltRemover(
    defnData="[Li,Be,B,Na,Mg,Al,Cl,K,Ca,Ti,Cr,Mn,Fe,Co,Ni,Cu,Zn,Ga,Br,Pd,Ag,Sn,I,Pt,Au,Pb]")


def cleanOneSmilesSimply(smiles: str) -> tuple:
    """
    process on smiles with default arguments
    @param smiles:
    @return: cleand_smiles, scaffolds
    """
    return processOneSmiles(smiles, _DEFAULT_REMOVER_TOOL,
                            chiral=True, remove_polymer=False, remove_inorganic=True)


def cleanSmilesListSimply(smilesList: list[str]) -> list[tuple]:
    """

    @param smilesList:
    @return: [(smiles, cleanedSmiles, scaffolds)]
    """
    ret = []
    for smiles in smilesList:
        cleanedSmiles, scaffolds = processOneSmiles(smiles, _DEFAULT_REMOVER_TOOL,
                                                    chiral=True, remove_polymer=False, remove_inorganic=True)
        ret.append((smiles, cleanedSmiles, scaffolds))
    return ret
