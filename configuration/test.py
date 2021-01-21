
category_model_averageOption_dict = {
    "A": {},
    "D": {},
    "M": {},
    "E": {},
    "T": {},
    "P": {},
}
with open('average_operation_in_radar.csv', 'r') as f:
    for line in f.readlines():
        rawData: list = line.strip().split(',')
        category_model: list = rawData[0].split('_')
        category = category_model[0]
        model = category_model[1]
        operation = int(rawData[1])
        category_model_averageOption_dict[category][model] = operation

print(category_model_averageOption_dict)
