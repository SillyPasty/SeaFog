from data_pros import get_dataset, sampling

from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import numpy as np

FILE_PATH = r'calipso\result_data\him_dataset'

# X, Y = get_dataset(FILE_PATH)

# np.savez(r'seafog_svm\dataset',x=X, y=Y)

dataset = np.load(r'seafog_svm\dataset.npz')
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

# X_train = X_train[:10000]
# y_train = y_train[:10000]
# X_test = X_test[:1000]
# y_test = y_test[:1000]
# Init model
svc = SVC(gamma='auto', tol=1e-5)

# Train
svc.fit(X_train, y_train)

# Predic on test set
y_pred = svc.predict(X_test)

print(mean_squared_error(y_test, y_pred))

print(classification_report(y_test, y_pred))

mat = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = mat.ravel()
print(mat)
