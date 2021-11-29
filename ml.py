# import pandas as pd
# import shap
# from joblib import dump, load
# pca = load('./Trained_Models/PCA.joblib')
# autenc = load('./Trained_Models/AutoEncoder.joblib')
# isofor = load('./Trained_Models/IsolatedForest.joblib')

# def prediction(record):
#     p = pca.predict(record)
#     i = isofor.predict(record)
#     a = autenc.predict(record)   
#     sum = p+i+a
#     return sum;

# def readFile(filePath):
#     f = open(filePath)
#     lines = f.readlines()

#     def convertLine(line):
#         data = line.replace('\n', '').split(':')
#         feature = data[0].strip()
#         value = data[1].strip()
#         if value.replace('.','',1).isdigit(): value = int(value)
#         return {feature: value}

#     lines = list(map(convertLine,lines))
#     lines.append({"Unnamed: 0": 12412});
#     lines.append({"Unnamed: 0.1": 12412});

#     data = {}
#     for line in lines: data.update(line)
#     data = pd.DataFrame([data])

#     # data = pd.read_csv(filePath)

#     def encoding(df):
#         df = df.where(pd.notnull(df), None)
#         X =  df.applymap(hash)
#         return X
#     data = encoding(data).iloc[-1]
#     return int(prediction([data])[0])

# # res = readFile("./static/uploads/mid_risk.csv")
# # print(res)
