from django.db import models


#     categoryField = CATEGORY_FIELD_NAME
#     modelNameField = 'uniprot_id'
#     geneSymbolField = 'gene_symbol'
#     geneNameField = 'Gene names'
#     diseaseProteinScoreField = 'score'
#     performanceField = 'AUROC'
#     diseaseClassNameField = "disease_class_name"
#     diseaseProteinScoreTypeField = "type"
# Create your models here.
class LBVSPerformanceFiltered(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')

    model = models.CharField(max_length=50)

    category = models.CharField(max_length=100)

    geneName = models.CharField(max_length=200)

    geneSymbol = models.CharField(max_length=200)

    performance = models.FloatField()

    diseaseClass = models.CharField(max_length=500)

    diseaseClassIndex = models.IntegerField(default=0)


# 没有使用继承，是因为在初始化是会调用bulk_create()，改方法无法处理继承的Model
class LBVSPerformanceRaw(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')

    model = models.CharField(max_length=50)

    category = models.CharField(max_length=100)

    geneName = models.CharField(max_length=200)

    geneSymbol = models.CharField(max_length=200)

    performance = models.FloatField()

    diseaseClass = models.CharField(max_length=500)

    diseaseClassIndex = models.IntegerField(default=0)

    diseaseProteinScore = models.FloatField()

    diseaseProteinScoreType = models.CharField(max_length=10)
