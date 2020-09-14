import pandas as pd
import numpy as np

rawDF: pd.DataFrame = pd.read_csv('training_viral_network_all_raw.csv')
rawDF.applymap(lambda x: x + 10.0 if (x is not np.nan and type(eval(x)) == float) else x)
print(rawDF)
predictDF: pd.DataFrame = pd.read_csv('training_viral_network_all.csv')

df = pd.merge(predictDF, rawDF, how='outer', on='cleaned_smiles', suffixes=("_pre", '_raw'))

print(df.values)

predictDF.update(rawDF)
