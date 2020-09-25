import pandas as pd
import numpy as np

rawDF: pd.DataFrame = pd.read_csv('training_viral_network_all_raw.csv')
dataDF = rawDF[rawDF.columns[1:]]
dataDF = dataDF.applymap(lambda x: x + 10.0 if (x is not np.nan) else x)
rawDF.update(dataDF)

predictDF: pd.DataFrame = pd.read_csv('training_viral_network_all.csv', float_precision='high')
predictDF.update(rawDF)

predictDF.to_csv("training_viral_network_final_result.csv", index=False)


# with open('filelist_admet.csv', 'r') as f:
#     lines = f.readlines()
#     for index, line in enumerate(lines):
#         records = line.strip().split('_', 1)
#         print(f'{records[0]}, "{records[1]}": {7100 + index},')
