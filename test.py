import math
import datetime
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
test_data = np.load('test.npy')
# print(info)
# print(info.shape)

# print(info[:2,:])

model = joblib.load(r'seafog_svm\model\svc\svm_day.pkl')
scaler = StandardScaler()
scaler.fit(test_data)
test_data = scaler.transform(test_data)
res = model.predict(test_data)
print(np.sum(res))