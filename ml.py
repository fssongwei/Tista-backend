import pandas as pd
from pymongo import database
import shap
import numpy as np
from joblib import dump, load
pca = load('./Trained_Models/PCA.joblib')
autenc = load('./Trained_Models/AutoEncoder.joblib')
isofor = load('./Trained_Models/IsolatedForest.joblib')

def prediction(record):
    p = pca.predict(record)
    i = isofor.predict(record)
    a = autenc.predict(record)   
    sum = p+i+a
    return sum[0];

def read_txt_file(file_path):
    with open(file_path,'r') as f:
        content = [item.strip() for item in f.readlines()]
        features = []
        for line in content:
            parts = line.split('\t')
            features.append(parts)
        data = pd.DataFrame(features, columns=['claim_id','provider_type', 'patient_id', 'billable_start', 'billable_end', 'bill_time_difference', 'provider_name','insurance_company', 'num_sequence', 'total_payment', 'encounter_des', 'net_value', 'service', 'total_visits', 'claims_per_provider'])
        return data.applymap(hash)



