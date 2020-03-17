from django import forms
from .sysConfig import SERVER_CONFIG_DICT


# format  ((value1, name1), (value1, name1))
modelChoices = tuple([(key, key) for key in SERVER_CONFIG_DICT.get("modelAndPort").keys()])


class ModelChoicesForm(forms.Form):

    modelTypes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           label="",
                                           required=True,
                                           choices=modelChoices)


class TextInputForm(ModelChoicesForm):

    t_smiles = forms.CharField(widget=forms.Textarea, label="", required=True,
                               max_length=2000)

    field_order = ['t_smiles', 'modelTypes']


class FileUploadForm(ModelChoicesForm):

    f_smiles = forms.FileField(widget=forms.FileInput, label="", required=True)

    field_order = ['f_smiles', 'modelTypes']
