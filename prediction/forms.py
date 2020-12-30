from django import forms
from .config import *
from deep_engine_client.forms import CommonInputForm

# format  [(value1, name1), (value1, name1)]
ligandModelChoices = tuple([(model, data[0]) for model, data in
                            PREDICTION_SERVER_MODEL_CFG.get(PREDICTION_TYPE_LIGAND).items()])
# format  [(value1, name1), (value1, name1)]
networkModelChoices = tuple([(model, data[0]) for model, data in
                             PREDICTION_SERVER_MODEL_CFG.get(PREDICTION_TYPE_NETWORK).items()])


class LigandModelInputForm(CommonInputForm):
    modelTypes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           label="",
                                           required=True,
                                           choices=ligandModelChoices,
                                           initial=ligandModelChoices[0])

    # field_order在html中体现了，使用{{ inputform.[fieldName] }}逐一展示
    # field_order = ['inputType', 'inputStr', 'uploadInputFile', 'modelTypes']


class NetworkModelInputForm(CommonInputForm):
    modelTypes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           label="",
                                           required=True,
                                           choices=networkModelChoices,
                                           initial=networkModelChoices[0])
