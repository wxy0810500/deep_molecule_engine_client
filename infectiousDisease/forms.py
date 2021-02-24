from django import forms
from .config import PREDICTION_SERVER_MODEL_CFG, PREDICTION_TYPE_STRUCTURE_BASED
from deep_engine_client.forms import CommonInputForm

# format  [(value1, name1), (value1, name1)]
_modelTypeChoices = tuple([(model, data[0]) for model, data in
                           PREDICTION_SERVER_MODEL_CFG.get(PREDICTION_TYPE_STRUCTURE_BASED).items()])


class InfectiousDiseaseInputForm(CommonInputForm):
    modelTypes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           label="",
                                           required=True,
                                           choices=_modelTypeChoices,
                                           initial=_modelTypeChoices[0])


    # field_order在html中体现了，使用{{ inputform.[fieldName] }}逐一展示
    # field_order = ['inputType', 'inputStr', 'uploadInputFile', 'modelTypes']
