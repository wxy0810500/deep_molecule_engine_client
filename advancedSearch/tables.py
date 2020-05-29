import django_tables2 as tables


class SearchResultTable(tables.Table):
    input = tables.Column(orderable=False, verbose_name="input(name|smiles)", attrs={
        "th": {
            "class": "c-input"
        },
        "td": {
            "class": "c-input"
        }
    })
    drug_name = tables.Column(orderable=False, verbose_name="Name", attrs={
        "th": {
            "class": "c-name"
        },
        "td": {
            "class": "c-name"
        }
    })
    ST_VIRUS = tables.Column(verbose_name="Virus", orderable=False, attrs={
        "th": {
            "class": "c-virus"
        },
        "td": {
            "class": "c-virus"
        }
    })
    PX = tables.Column(verbose_name="PX", orderable=False, attrs={
        "th": {
            "class": "c-px"
        },
        "td": {
            "class": "c-px"
        }
    })
    cleaned_smiles = tables.Column(verbose_name="Cleaned smiles", orderable=False, attrs={
        "th": {
            "class": "c-cs"
        },
        "td": {
            "class": "c-cs"
        }
    })
    scaffolds = tables.Column(verbose_name="Scaffolds", orderable=False, attrs={
        "th": {
            "class": "c-scaffolds"
        },
        "td": {
            "class": "c-scaffolds"
        }
    })
