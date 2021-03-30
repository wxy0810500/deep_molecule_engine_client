import django_tables2 as tables


class PredictionResultTable(tables.Table):
    counter = tables.TemplateColumn("{{ row_counter|add:1 }}", verbose_name="")
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
    drugName = tables.Column(orderable=False, verbose_name="Drug name", attrs={
        "th": {
            "class": "c-drugName"
        },
        "td": {
            "class": "c-drugName"
        }
    })
    cleanedSmiles = tables.Column(orderable=False, verbose_name="Cleaned smiles", attrs={"td": {
        "class": "cleaned-smiles"
    }
    })

    class Meta:
        attrs = {
            "class": "blueTable"
        }


