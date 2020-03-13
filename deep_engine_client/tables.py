import django_tables2 as tables


class SmilesResultTable(tables.Table):
    err_code = tables.Column()
    result = tables.Column()
    SMILES = tables.Column()


class MultiModelResultTables(tables.MultiTableMixin):
    template_name = "result.html"

    def __init__(self, tables_data, modelType):
        self.tables_data = tables_data
        self.modelType = modelType

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tables = self.get_tables()

        # apply prefixes and execute requestConfig for each table
        for table in tables:
            table.prefix = self.modelType

            # RequestConfig(self.request, paginate=self.get_table_pagination(table)).configure(table)
            context[self.get_context_table_name(table)] = list(tables)

        return context