import django_tables2 as tables


class InvalidInputsTable(tables.Table):
    input = tables.Column(orderable=False, verbose_name="invalid input(name|smiles)", attrs={
        "th": {
            "class": "c-invalid-input"
        },
        "td": {
            "class": "c-invalid-input"
        }
    })

    @staticmethod
    def getInvalidInputsTable(invalidInputList):
        return InvalidInputsTable([{'input': invalidInput} for invalidInput in invalidInputList])

