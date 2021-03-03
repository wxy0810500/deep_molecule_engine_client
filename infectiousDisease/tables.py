import django_tables2 as tables
import itertools


class PredictionResultTable(tables.Table):
    counter = tables.TemplateColumn("{{ row_counter|add:1 }}", verbose_name="")
    # counter = tables.Column(empty_values=(), orderable=False)
    #
    # def render_counter(self):
    #     self.row_counter = getattr(self, 'row_counter', itertools.count())
    #     return next(self.row_counter)
    modelName = tables.Column(orderable=False, verbose_name="Model Name", attrs={
        "th": {
            "class": "modelName_th"
        },
        "td": {
            "class": "modelName_td"
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


