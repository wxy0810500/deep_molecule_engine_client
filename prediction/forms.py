from django import forms
from deep_engine_client.forms import CommonInputForm
from .models import LBVSPerformanceRaw
import sys

if len(sys.argv) > 1 and sys.argv[1] != 'runserver':
    class TFModelInputForm(CommonInputForm):
        pass
else:
    # get all categorys and disease classes
    allCategorys = LBVSPerformanceRaw.objects.values_list('category').distinct()
    allDiseaseClass = LBVSPerformanceRaw.objects.values_list('diseaseClass', 'diseaseClassIndex').distinct()

    # format  [(value1, name1), (value1, name1)]
    ADMET_categorys = tuple([(category[0], category[0]) for category in allCategorys])
    diseaseClassNameTuple = tuple([(record[1], record[0]) for record in allDiseaseClass])


    class TFModelInputForm(CommonInputForm):
        categorys = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                              label="",
                                              required=False,
                                              choices=ADMET_categorys,
                                              initial=ADMET_categorys[0])
        diseaseClasses = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                   label="",
                                                   required=False,
                                                   choices=diseaseClassNameTuple,
                                                   initial=diseaseClassNameTuple[0])

        # field_order在html中体现了，使用{{ inputform.[fieldName] }}逐一展示
        # field_order = ['inputType', 'inputStr', 'uploadInputFile', 'modelTypes']
