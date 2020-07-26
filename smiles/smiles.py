class SmilesData:

    def __init__(self, smiles: str, drugName: str, cleanedSmiles: str, scaffolds: str):
        self.smiles = smiles
        self.drugName = drugName
        self.cleanedSmiles = cleanedSmiles
        self.scaffolds = scaffolds
