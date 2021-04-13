import django_tables2 as tables


class PredictionResultTable(tables.Table):
    model = tables.Column(orderable=False, verbose_name="Model name", attrs={
        "th": {
            "class": "model_th"
        },
        "td": {
            "class": "model_td"
        }
    })

    score = tables.Column(orderable=False, verbose_name="Score", attrs={
        "th": {
            "class": "score_th"
        },
        "td": {
            "class": "score_td"
        }
    })
    geneName = tables.Column(orderable=False, verbose_name="Gene Name", attrs={
        "th": {
            "class": "geneName_th"
        },
        "td": {
            "class": "geneName_td"
        }
    })
    geneSymbol = tables.Column(orderable=False, verbose_name="Gene Symbol", attrs={
        "th": {
            "class": "geneSymbol_th"
        },
        "td": {
            "class": "geneSymbol_td"
        }
    })
    performance = tables.Column(orderable=False, verbose_name="Performance", attrs={
        "th": {
            "class": "performance_th"
        },
        "td": {
            "class": "performance_td"
        }
    })
    diseaseClasses = tables.Column(orderable=False, verbose_name="Disease Classes", attrs={
        "th": {
            "class": "diseaseClasses_th"
        },
        "td": {
            "class": "diseaseClasses_td"
        }
    })

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


