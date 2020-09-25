from django import forms
from deep_engine_client.sysConfig import SERVER_CONFIG_DICT
from deep_engine_client.forms import CommonInputForm

# format  [(value1, name1), (value1, name1)]
ADMET_model_types = tuple([(model, data[0]) for model, data in
                           SERVER_CONFIG_DICT.get("modelAndPort").items()])


class ADMETModelInputForm(CommonInputForm):
    modelTypes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           label="",
                                           required=True,
                                           choices=ADMET_model_types,
                                           initial=ADMET_model_types[0])

    # field_order在html中体现了，使用{{ inputform.[fieldName] }}逐一展示
    # field_order = ['inputType', 'inputStr', 'uploadInputFile', 'modelTypes']
