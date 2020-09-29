import django_tables2 as tables


class PredictionResultTable(tables.Table):
    id = tables.Column(verbose_name="", orderable=False, attrs={
        "th": {
            "class": "c-id"
        },
        "td": {
            "class": "c-id"
        }
    })
    score = tables.Column(orderable=False, verbose_name="Score", attrs={
        "th": {
            "class": "c-score"
        },
        "td": {
            "class": "c-score"
        }
    })
    # label = tables.Column(orderable=False, attrs={
    #     "th": {
    #         "class": "c-label"
    #     },
    #     "td": {
    #         "class": "c-label"
    #     }
    # })
    input = tables.Column(orderable=False, verbose_name="Input{name|smiles}", attrs={
        "th": {
            "class": "c-input"
        },
        "td": {
            "class": "c-input"
        }
    })
    drugName = tables.Column(orderable=False, verbose_name="drug_name", attrs={
        "th": {
            "class": "c-drugName"
        },
        "td": {
            "class": "c-drugName"
        }
    })
    cleanedSmiles = tables.Column(orderable=False, verbose_name="cleaned_smiles", attrs={
        "td": {
            "class": "cleaned-smiles"
        }
    })

    class Meta:
        attrs = {
            "class": "blueTable"
        }


class NetworkBasedResultTable(tables.Table):
    score = tables.Column(orderable=False, verbose_name="Score")
    input = tables.Column(orderable=False, verbose_name="Input{name|smiles}")
    drugName = tables.Column(orderable=False, verbose_name="drug_name")
    cleanedSmiles = tables.Column(orderable=False, verbose_name="cleaned_smiles", attrs={
        "td": {
            "class": "cleaned-smiles"
        }
    })

    class Meta:
        attrs = {
            "class": "blueTable"
        }
