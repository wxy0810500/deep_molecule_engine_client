import django_tables2 as tables


class SmilesResult(tables.Table):

    class Meta:
        template_name = 'result.html'