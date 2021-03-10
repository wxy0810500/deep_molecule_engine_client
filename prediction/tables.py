import django_tables2 as tables


class PredictionResultTable(tables.Table):
    model = tables.Column(orderable=False, verbose_name="model", attrs={
        "th": {
            "class": "model_th"
        },
        "td": {
            "class": "model_td"
        }
    })

    score = tables.Column(orderable=False, verbose_name="probability",
                          attrs={
                              "th": {
                                  "class": "probability_th"
                              },
                              "td": {
                                  "class": "probability_td"
                              }
                          })
    scoreForAve = tables.Column(orderable=False, verbose_name="drug-like score contribution",
                                attrs={
                                    "th": {
                                        "class": "drug_like_score_th"
                                    },
                                    "td": {
                                        "class": "drug_like_score_td"
                                    }
                                })

    class Meta:
        attrs = {
            "class": "blueTable score"
        }


class PredictionResultSmilesInfoTable(tables.Table):
    columns = ['Input(name|smiles)', 'Drug Name', 'Cleaned SMILES']
    input = tables.Column(orderable=False, verbose_name="Input(name|smiles)")
    drug_name = tables.Column(orderable=False, verbose_name="Drug Name")
    cleaned_smiles = tables.Column(verbose_name="Cleaned SMILES", orderable=False, attrs={
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
