from deep_engine_client.forms import TextInputForm
from smiles.searchService import searchDrugReferenceByCleanedSmiles

inputStr = "Timolol,Treprostinil,Colestipol,Trihexyphenidyl,Palonosetron,Dydrogesterone"
inputDrugNameList = TextInputForm.filterInputDrugNames(inputStr)

drugRefDF = searchDrugReferenceByCleanedSmiles(inputDrugNameList)
# 加入input 列
drugRefDF['input'] = inputDrugNameList

print(1)