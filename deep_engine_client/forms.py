from django import forms
import re
from typing import List
from .fields import RestrictedFileField


class CommonInputForm(forms.Form):
    INPUT_TYPE_DRUG_NAME = 'drugName'
    INPUT_TYPE_SMILES = 'raw_smiles'
    OUTPUT_TYPE_FILE = 'file'
    OUTPUT_TYPE_WEB_PAGE = 'webPage'
    INPUT_NAME_STR_SEPARATOR_RX = '!|,|;|\t|\n|\r\n'
    INPUT_SMILES_STR_SEPARATOR_RX = '!|,|;|\t|\n|\r\n| '
    MAX_SMILES_LEN: int = 500

    inputType = forms.ChoiceField(widget=forms.RadioSelect, label="", required=True,
                                  choices=[(INPUT_TYPE_DRUG_NAME, 'DRUG_NAMES'), (INPUT_TYPE_SMILES, 'SMILES')],
                                  initial=[INPUT_TYPE_SMILES], )
    inputStr = forms.CharField(widget=forms.Textarea, label="", max_length=2000, required=False, )
    # error_messages={"required": "Please enter the SMILES or "
    #                             "NAMES of your compound, one per line"})

    uploadInputFile = RestrictedFileField(widget=forms.FileInput(attrs={
        "onchange": "document.getElementById('inputFileName').innerText=this.files[0].name"
    }), required=False, label="", max_upload_size=2621440,)  # 2.5M

    outputType = forms.ChoiceField(widget=forms.RadioSelect, label="", required=True,
                                   choices=[(OUTPUT_TYPE_FILE, 'download results as csv file'),
                                            (OUTPUT_TYPE_WEB_PAGE, 'show results on the website')],
                                   initial=[OUTPUT_TYPE_WEB_PAGE], )

    @classmethod
    def splitAndFilterInputSmiles(cls, smiles: str) -> List[str]:
        return [smiles.strip() for smiles in set(re.split(cls.INPUT_SMILES_STR_SEPARATOR_RX, smiles.strip()))
                if (cls.MAX_SMILES_LEN > len(smiles) > 0)]

    @classmethod
    def splitAndFilterInputDrugNamesStr(cls, drugNames: str) -> List[str]:
        return [name.strip().lower() for name in set(re.split(cls.INPUT_NAME_STR_SEPARATOR_RX, drugNames.strip()))]
