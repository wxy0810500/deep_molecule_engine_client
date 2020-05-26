from django import forms
from .sysConfig import SERVER_CONFIG_DICT

# format  [(value1, name1), (value1, name1)]
ligandModelChoices = tuple([(model, data[0]) for model, data in
                            SERVER_CONFIG_DICT.get("modelAndPort").get("ligand").items()])
structureModelChoices = tuple([(model, data[0]) for model, data in
                               SERVER_CONFIG_DICT.get("modelAndPort").get("structure").items()])


class TextInputForm(forms.Form):
    inputType = forms.ChoiceField(widget=forms.RadioSelect, label="", required=True,
                                  choices=[('name', 'name'), ('smiles', 'smiles')], initial=['smiles'])
    inputStr = forms.CharField(widget=forms.Textarea, label="", max_length=2000)