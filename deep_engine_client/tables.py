import django_tables2 as tables


class SmilesResultTable(tables.Table):
    err_code = tables.Column()
    result = tables.Column()
    SMILES = tables.Column()
