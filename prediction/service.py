from typing import Tuple, List

from prediction.forms import CommonInputForm
from smiles.searchService import searchDrugReferenceByInputRequest


def getCleanedSmilesInfoListFromInputForm(inputForm: CommonInputForm, request) -> Tuple[List[dict], List[str]]:
    drugRefDF, invalidInputList = searchDrugReferenceByInputRequest(request, inputForm)
    if drugRefDF.size == 0:
        return None, invalidInputList
    return drugRefDF[['input', 'drug_name', 'cleaned_smiles']].to_dict(orient='records'), invalidInputList
