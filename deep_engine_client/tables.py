import django_tables2 as tables


class SmilesResultTable(tables.Table):
    id = tables.Column(verbose_name="", orderable=False, attrs={
        "th": {
            "class": "c-id"
        },
        "td": {
            "class": "c-id"
        }
    })
    score = tables.Column(orderable=False, verbose_name="active score", attrs={
        "th": {
            "class": "c-score"
        },
        "td": {
            "class": "c-score"
        }
    })
    label = tables.Column(orderable=False, attrs={
        "th": {
            "class": "c-label"
        },
        "td": {
            "class": "c-label"
        }
    })
    smiles = tables.Column(orderable=False, attrs={
        "th": {
            "class": "c-smiles"
        },
        "td": {
            "class": "c-smiles"
        }
    })
