from django import forms
from .modelConfig import MODEL_TYPE_STATMENT_DICT
from prediction.forms import CommonInputForm


# format  [(value1, name1), (value1, name1)]

class InfectiousDiseaseInputForm(CommonInputForm):
    __modelTypeChoices = tuple([(model, f'{model}:{statement}') for model, statement in
                                MODEL_TYPE_STATMENT_DICT.items()])
    # __metricsChoices = tuple([(metrics, name) for metrics, name in PREDICTION_METRICS_NAME_DICT.items()])

    modelTypes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           label="",
                                           required=True,
                                           choices=__modelTypeChoices,
                                           initial=__modelTypeChoices[0])

    # metric = forms.ChoiceField(widget=forms.RadioSelect,
    #                            label="",
    #                            required=True,
    #                            choices=__metricsChoices,
    #                            initial=__metricsChoices[0])
    # field_order在html中体现了，使用{{ inputform.[fieldName] }}逐一展示
    # field_order = ['inputType', 'inputStr', 'uploadInputFile', 'modelTypes']
