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
    label = tables.Column(orderable=False, attrs={
        "th": {
            "class": "c-label"
        },
        "td": {
            "class": "c-label"
        }
    })
    ratings = tables.Column(orderable=False, verbose_name="Predicted ratings", attrs={
        "th": {
            "class": "c-ratings"
        },
        "td": {
            "class": "c-ratings"
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
