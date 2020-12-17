from django import forms
from configuration.sysConfig import PREDICTION_CATEGORY_NAME_DICT, PREDICTION_METRICS_NAME_DICT
from deep_engine_client.forms import CommonInputForm


# format  [(value1, name1), (value1, name1)]


class ADMETModelInputForm(CommonInputForm):
    __ADMET_categorys = tuple([(tag, category) for tag, category in PREDICTION_CATEGORY_NAME_DICT.items()])
    __ADMET_metrics = tuple([(name, metrics) for metrics, name in PREDICTION_METRICS_NAME_DICT.items()])

    categorys = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                          label="",
                                          required=True,
                                          choices=__ADMET_categorys,
                                          initial=__ADMET_categorys[0])

    metric = forms.ChoiceField(widget=forms.RadioSelect,
                               label="",
                               required=True,
                               choices=__ADMET_metrics,
                               initial=__ADMET_metrics[0])

    # field_order在html中体现了，使用{{ inputform.[fieldName] }}逐一展示
    # field_order = ['inputType', 'inputStr', 'uploadInputFile', 'modelTypes']
