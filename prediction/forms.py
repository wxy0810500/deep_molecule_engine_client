from django import forms
from deep_engine_client.sysConfig import SERVER_CONFIG_DICT
from deep_engine_client.forms import CommonInputForm

# format  [(value1, name1), (value1, name1)]
ligandModelChoices = tuple([(model, data[0]) for model, data in
                            SERVER_CONFIG_DICT.get("modelAndPort").get("ligand").items()])
structureModelChoices = tuple([(model, data[0]) for model, data in
                               SERVER_CONFIG_DICT.get("modelAndPort").get("structure").items()])
networkModelChoices = tuple([(model, data[0]) for model, data in
                             SERVER_CONFIG_DICT.get("modelAndPort").get("network").items()])


class LigandModelInputForm(CommonInputForm):
    modelTypes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           label="",
                                           required=True,
                                           choices=ligandModelChoices,
                                           initial=ligandModelChoices[0])

    # field_order在html中体现了，使用{{ inputform.[fieldName] }}逐一展示
    # field_order = ['inputType', 'inputStr', 'uploadInputFile', 'modelTypes']


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


class NetworkModelInputForm(CommonInputForm):
    modelTypes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           label="",
                                           required=True,
                                           choices=networkModelChoices,
                                           initial=networkModelChoices[0])
