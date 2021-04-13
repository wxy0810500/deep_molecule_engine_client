import pandas as pd
import os
from deep_engine_client.settings.base import BASE_DIR
from prediction.models import LBVSPerformanceFiltered, LBVSPerformanceRaw

CATEGORY_FIELD_NAME = 'protein_class_name'


def initLBVSPerformanceDB():
    rawDF = pd.read_csv(os.path.join(BASE_DIR, "prediction/db/LBVS_performance_table.csv"))
    categoryField = CATEGORY_FIELD_NAME
    modelNameField = 'uniprot_id'
    geneSymbolField = 'gene_symbol'
    geneNameField = 'Gene names'
    diseaseProteinScoreField = 'score'
    performanceField = 'AUROC'
    diseaseClassNameField = "disease_class_name"
    diseaseProteinScoreTypeField = "type"

    rawTableDF: pd.DataFrame = rawDF[[categoryField, modelNameField, performanceField, geneSymbolField, geneNameField,
                                      diseaseClassNameField, diseaseProteinScoreField, diseaseProteinScoreTypeField]]
    # 提取所有的disease_protein_class
    diseaseClassNameDF = rawDF[[diseaseClassNameField]].drop_duplicates()
    diseaseClassNameDF.reset_index(inplace=True, drop=True)
    """
        为每个disease分配一个数字作为Index，查询等操作均用index来进行
        1. 创建DataFrame
           classIndex, className
            1        , xxxx
            2        , xxxx
        2. 与tableDF进行join,为每个record添加diseaseClassIndex列
        3. 入参category及diseaseClassIndex获取model performanceinfo
    """
    diseaseClassIndexField = 'diseaseClassIndex'
    diseaseClassIndexDF = pd.DataFrame(
        {diseaseClassIndexField: [i for i in range(1, len(diseaseClassNameDF.index) + 1, 1)]})
    diseaseClassDF = diseaseClassNameDF.join(diseaseClassIndexDF)
    rawTableDF = rawTableDF.merge(diseaseClassDF, on=diseaseClassNameField, how="left")
    rawTableDF.reset_index(inplace=True, drop=True)
    # filter: diseaseProteinScoreType == maximun && score > 0.1
    tableDF = rawTableDF[(rawTableDF[diseaseProteinScoreTypeField] == 'maximum') &
                         (rawTableDF[diseaseProteinScoreField] > 0.1)]

    tableDF.reset_index(inplace=True, drop=True)
    tableDF.drop([diseaseProteinScoreTypeField, diseaseProteinScoreField], axis=1, inplace=True)
    # save rawTableDF to LBVSPerformanceRaw
    dfRecords = rawTableDF.to_dict("records")
    modelInstances = [LBVSPerformanceRaw(category=record[categoryField], model=record[modelNameField],
                                         geneName=record[geneNameField], geneSymbol=record[geneSymbolField],
                                         diseaseClass=record[diseaseClassNameField],
                                         diseaseClassIndex=record[diseaseClassIndexField],
                                         performance=record[performanceField],
                                         diseaseProteinScore=record[diseaseProteinScoreField],
                                         diseaseProteinScoreType=record[diseaseProteinScoreTypeField])
                      for record in dfRecords]
    LBVSPerformanceRaw.objects.bulk_create(modelInstances)
    # save filtered tableDF to LBVSPerformanceFiltered
    dfRecords = tableDF.to_dict("records")
    modelInstances = [LBVSPerformanceFiltered(category=record[categoryField], model=record[modelNameField],
                                              geneName=record[geneNameField], geneSymbol=record[geneSymbolField],
                                              diseaseClass=record[diseaseClassNameField],
                                              performance=record[performanceField],
                                              diseaseClassIndex=record[diseaseClassIndexField])
                      for record in dfRecords]
    LBVSPerformanceFiltered.objects.bulk_create(modelInstances)
