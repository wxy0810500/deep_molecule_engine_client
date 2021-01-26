import django_tables2 as tables


class PredictionResultTable(tables.Table):
    model = tables.Column(orderable=False, attrs={
        "th": {
            "class": "model_th"
        },
        "td": {
            "class": "model_td"
        }
    })

    score = tables.Column(orderable=False, attrs={
        "th": {
            "class": "score_th"
        },
        "td": {
            "class": "score_td"
        }
    })
    # scoreForAve = tables.Column(orderable=False, attrs={
    #     "th": {
    #         "class": "score_th"
    #     },
    #     "td": {
    #         "class": "score_td"
    #     }
    # })

    class Meta:
        attrs = {
            "class": "blueTable score"
        }


class PredictionResultSmilesInfoTable(tables.Table):
    columns = ['Input(name|smiles)', 'DrugName', 'Cleaned smiles']
    input = tables.Column(orderable=False, verbose_name="Input(name|smiles)")
    drug_name = tables.Column(orderable=False, verbose_name="DrugName")
    cleaned_smiles = tables.Column(verbose_name="Cleaned smiles", orderable=False, attrs={
        "th": {
            "class": "c-cs"
        },
        "td": {
            "class": "c-cs"
        }
    })

    class Meta:
        attrs = {
            "class": "blueTable smiles-info"
        }


