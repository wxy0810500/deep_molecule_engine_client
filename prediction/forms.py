from django import forms
from .config import PREDICTION_SERVER_MODEL_CFG, PREDICTION_TYPE_STRUCTURE_BASED
from deep_engine_client.forms import CommonInputForm

# format  [(value1, name1), (value1, name1)]
structureModelChoices = tuple([(model, data[0]) for model, data in
                               PREDICTION_SERVER_MODEL_CFG.get(PREDICTION_TYPE_STRUCTURE_BASED).items()])


class StructureModelInputForm(CommonInputForm):
    modelTypes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           label="",
                                           required=True,
                                           choices=structureModelChoices,
                                           initial=structureModelChoices[0])

    uploadPDBFile = forms.FileField(widget=forms.FileInput(attrs={
        "onchange": "document.getElementById('pdbFileName').innerText=this.files[0].name"
    }), label="", required=True)

    # field_order在html中体现了，使用{{ inputform.[fieldName] }}逐一展示
    # field_order = ['inputType', 'inputStr', 'uploadInputFile', 'modelTypes']
