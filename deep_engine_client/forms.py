from django import forms
from .sysConfig import SERVER_CONFIG_DICT

# format  ((value1, name1), (value1, name1))
ligandModelChoices = tuple([(model, data[0]) for model, data in
                            SERVER_CONFIG_DICT.get("modelAndPort").get("ligand").items()])
structureModelChoices = tuple([(model, data[0]) for model, data in
                               SERVER_CONFIG_DICT.get("modelAndPort").get("structure").items()])


class TextInputForm(forms.Form):
    t_smiles = forms.CharField(widget=forms.Textarea, label="", max_length=2000)
    t_names = forms.CharField(widget=forms.Textarea, label="", max_length=2000)


class LigandModelChoicesForm(TextInputForm):
    modelTypes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           label="",
                                           required=True,
                                           choices=ligandModelChoices)

    field_order = ['t_smiles', 't_names', 'modelTypes']


class StructureModelChoicesForm(TextInputForm):
    modelTypes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           label="",
                                           required=True,
                                           choices=structureModelChoices)

    field_order = ['t_smiles', 't_names', 'modelTypes']


class StructurePdbFileUploadForm(forms.Form):
    f_smiles = forms.FileField(widget=forms.FileInput, label="", required=True)
    modelTypes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           label="",
                                           required=True,
                                           choices=structureModelChoices)

    field_order = ['f_smiles', 'modelTypes']
