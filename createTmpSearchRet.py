import pandas as pd
import smiles.searchService as search

cleanedSmilesDF = pd.read_csv('cleaned_smiles.csv')

virusDF = pd.read_csv('advancedSearch/db/broad_spectrum_antiviral.csv')

cleanedDataDF = search.searchDrugReferenceByCleanedSmiles(cleanedSmilesDF)
scaffoldDataDF = search.queryDrugReferenceByScaffold(cleanedSmilesDF)


exactMapDF = pd.merge(virusDF[['PX', 'ST_VIRUS', 'cleaned_smiles', "scaffolds"]],
                      cleanedDataDF[['drug_name', 'SMILES', 'cleaned_smiles']],
                    on='cleaned_smiles', how='inner')

scaffoldMapDF = pd.merge(virusDF[['PX', 'ST_VIRUS', 'scaffolds', 'cleaned_smiles']],
                         scaffoldDataDF[['drug_name', 'SMILES', 'scaffolds']],
                         on='scaffolds', how='inner')

exactMapDF.rename(columns={'SMILES': 'input'})
# exactMapDF.to_csv('exactMap.csv', index=False)
# scaffoldMapDF.to_csv('scaffoldMap.csv', index=False)
