from django import forms
from .sysConfig import SERVER_CONFIG_DICT
import re
from typing import List

# format  [(value1, name1), (value1, name1)]
ligandModelChoices = tuple([(model, data[0]) for model, data in
                            SERVER_CONFIG_DICT.get("modelAndPort").get("ligand").items()])
structureModelChoices = tuple([(model, data[0]) for model, data in
                               SERVER_CONFIG_DICT.get("modelAndPort").get("structure").items()])


class TextInputForm(forms.Form):
    INPUT_TYPE_DRUG_NAME = 'drugName'
    INPUT_TYPE_SMILES = 'raw_smiles'
    INPUT_STR_SEPARATOR_RX = '!|,|;|\t|\n|\r\n| '
    MAX_SMILES_LEN: int = 500

    inputType = forms.ChoiceField(widget=forms.RadioSelect, label="", required=True,
                                  choices=[(INPUT_TYPE_DRUG_NAME, 'drug_name'), (INPUT_TYPE_SMILES, 'smiles')],
                                  initial=[INPUT_TYPE_SMILES])
    inputStr = forms.CharField(widget=forms.Textarea, label="", max_length=2000)

    @classmethod
    def filterInputSmiles(cls, smiles: str) -> List[str]:
        smilesList = re.split(cls.INPUT_STR_SEPARATOR_RX, smiles.strip())
        return [smiles.strip() for smiles in smilesList if (cls.MAX_SMILES_LEN > len(smiles) > 0)]

    @classmethod
    def filterInputDrugNames(cls, drugNames: str) -> List[str]:
        nameList = re.split(cls.INPUT_STR_SEPARATOR_RX, drugNames.strip())
        return [name.strip().lower() for name in nameList]
