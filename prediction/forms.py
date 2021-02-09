from django import forms
from configuration.sysConfig import PREDICTION_CATEGORY_MODEL_DICT
from deep_engine_client.forms import CommonInputForm

# format  [(value1, name1), (value1, name1)]
ADMET_categorys = tuple([(category, category) for category in PREDICTION_CATEGORY_MODEL_DICT.keys()])


class TFModelInputForm(CommonInputForm):
    categorys = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                          label="",
                                          required=True,
                                          choices=ADMET_categorys,
                                          initial=ADMET_categorys[0])

    # field_order在html中体现了，使用{{ inputform.[fieldName] }}逐一展示
    # field_order = ['inputType', 'inputStr', 'uploadInputFile', 'modelTypes']
