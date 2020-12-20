from django import forms
from .config import PREDICTION_SERVER_MODEL_CFG, PREDICTION_TYPE_STRUCTURE_BASED
from deep_engine_client.forms import CommonInputForm

# format  [(value1, name1), (value1, name1)]
structureModelChoices = tuple([(model, data[0]) for model, data in
                               PREDICTION_SERVER_MODEL_CFG.get(PREDICTION_TYPE_STRUCTURE_BASED).items()])


class StructureModelInputForm(CommonInputForm):
    PDB_FILE_TYPE_PROTEIN = "protein"
    PDB_FILE_TYPE_POCKET = "pocket"
    modelTypes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           label="",
                                           required=True,
                                           choices=structureModelChoices,
                                           initial=structureModelChoices[0])
    pdbFileType = forms.ChoiceField(widget=forms.RadioSelect(attrs={
                                        'onclick': "alert('foo !');",
                                    }), label="", required=True,
                                    choices=[(PDB_FILE_TYPE_PROTEIN, "protein pdb"),
                                             (PDB_FILE_TYPE_POCKET, "pocket pdb + pocket center coordinate (x, y, z)")],
                                    initial=[PDB_FILE_TYPE_PROTEIN],)

    uploadPDBFile = forms.FileField(widget=forms.FileInput(attrs={
        "onchange": "document.getElementById('pdbFileName').innerText=this.files[0].name"
    }), label="", required=True, error_messages={'required': 'Please select a pdb file'})
    cx = forms.FloatField(required=False)
    cy = forms.FloatField(required=False)
    cz = forms.FloatField(required=False)

    # field_order在html中体现了，使用{{ inputform.[fieldName] }}逐一展示
    # field_order = ['inputType', 'inputStr', 'uploadInputFile', 'modelTypes']
