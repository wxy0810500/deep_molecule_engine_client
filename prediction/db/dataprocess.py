import pandas as pd
import numpy as np

rawDF: pd.DataFrame = pd.read_csv('training_viral_network_all_raw.csv')
dataDF = rawDF[rawDF.columns[1:]]
dataDF = dataDF.applymap(lambda x: x + 10.0 if (x is not np.nan) else x)
rawDF.update(dataDF)

predictDF: pd.DataFrame = pd.read_csv('training_viral_network_all.csv', float_precision='high')
predictDF.update(rawDF)

predictDF.to_csv("training_viral_network_final_result.csv", index=False)