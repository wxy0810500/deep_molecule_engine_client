from django import forms
from deep_engine_client.sysConfig import SERVER_CONFIG_DICT
from deep_engine_client.forms import TextInputForm

# format  [(value1, name1), (value1, name1)]
ligandModelChoices = tuple([(model, data[0]) for model, data in
                            SERVER_CONFIG_DICT.get("modelAndPort").get("ligand").items()])
structureModelChoices = tuple([(model, data[0]) for model, data in
                               SERVER_CONFIG_DICT.get("modelAndPort").get("structure").items()])


class LigandModelChoicesForm(TextInputForm):
    modelTypes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           label="",
                                           required=True,
                                           choices=ligandModelChoices,
                                           initial=ligandModelChoices[0])

    field_order = ['inputType', 'inputStr', 'modelTypes']


class StructureInputForm(TextInputForm):
    modelTypes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           label="",
                                           required=True,
                                           choices=structureModelChoices,
                                           initial=structureModelChoices[0])

    field_order = ['inputType', 'inputStr', 'modelTypes']


class StructurePDBFileForm(forms.Form):
    uploadFile = forms.FileField(widget=forms.FileInput(attrs={
        "onchange": "document.getElementById('fileName').innerText=this.files[0].name"
    }), label="", required=True)
