from django import forms

# format  ((value1, name1), (value1, name1))
modelChoices = (('normal', 'normal1'), ('normal', 'normal2'))


class ModelChoicesForm(forms.Form):

    modelTypes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           label="",
                                           required=True,
                                           choices=modelChoices)


class TextInputForm(ModelChoicesForm):

    t_smiles = forms.CharField(widget=forms.Textarea, label="", required=True)

    field_order = ['t_smiles', 'modelTypes']


class FileUploadForm(ModelChoicesForm):

    f_smiles = forms.FileField(widget=forms.FileInput, label="", required=True)

    field_order = ['f_smiles', 'modelTypes']
