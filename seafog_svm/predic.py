from data_pros import get_dataset, sampling, get_filtered_dataset

from sklearn.svm import SVC, LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import numpy as np
import time
FILE_PATH = r'calipso\result_data\him_dataset'
start_time = time.time()
# X, Y = get_dataset(FILE_PATH)
# dataset = get_filtered_dataset(FILE_PATH)

# tags = ['sea_d', 'sea_n', 'land_d', 'land_n']

# for tag in tags:
#     np.savez(r'seafog_svm\dataset_' + tag,x=dataset[tag]['x'], y=dataset[tag]['y'])

dataset = np.load(r'seafog_svm\dataset_sea_d.npz')
X = dataset['x']
Y = dataset['y']
X, Y = sampling(X, Y)

Y = Y.ravel()
print(X.shape, Y.shape)

# Normalization
scaler = StandardScaler()
scaler.fit(X)
trans_X = scaler.transform(X)

# Split the dataset
X_train,X_test, y_train, y_test = train_test_split(trans_X, Y, test_size=0.2, random_state=0)

# Init model
svc = SVC(gamma='auto', tol=1e-5)
# svc = LinearSVC(tol=1e-5)

# Train
svc.fit(X_train, y_train)

# Predic on test set
y_pred = svc.predict(X_test)

print(mean_squared_error(y_test, y_pred))

print(classification_report(y_test, y_pred))

mat = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = mat.ravel()
print(mat)

print('Total time:' + str(time.time() - start_time))