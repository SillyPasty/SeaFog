from data_pros import get_dataset, sampling, get_filtered_dataset
from anal_error import get_error_anal

from sklearn.svm import SVC, LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.externals import joblib
from plot_learning_curve import plot_learning_curve
import numpy as np
import time
import os

def gen_dataset(latlon_range, lat1=45, lon1=105, lat2=18, lon2=150):
    FILE_PATH = r'calipso\result_data\him_dataset'
    print('Processing data...')
    dataset = get_filtered_dataset(FILE_PATH, lat1, lon1, lat2, lon2)
    tags = ['sea_d', 'sea_n', 'land_d', 'land_n']
    for tag in tags:
        np.savez(r'seafog_svm\data\dataset_' + tag + '_' + latlon_range,x=dataset[tag]['x'], y=dataset[tag]['y'])

def train(area, sea, land, day, night):
    latlon_range = ''
    if area != 'all':
        lat1, lon1 = 41, 117.5
        lat2, lon2 = 34, 127
        latlon_range = '_{}_{}_{}_{}'.format(lat1, lon1, lat2, lon2)
        # gen_dataset(latlon_range, lat1, lon1, lat2, lon2)
    else:
        latlon_range = ''
        # gen_dataset(latlon_range)

    print('Reading data...')
    dataset = {}
    tags = ['_sea_d', '_sea_n', '_land_d', '_land_n']
    for tag in tags:
        dataset_path = os.path.join('seafog_svm', 'data', 'dataset' + tag + latlon_range)
        dataset[tag] = np.load(dataset_path + '.npz')
    
    X = None
    Y = None

    if sea and day:
        tmp_x, tmp_y = dataset['_sea_d']['x'], dataset['_sea_d']['y']
        X = tmp_x if X is None else np.concatenate((X, tmp_x), axis=0)
        Y = tmp_y if Y is None else np.concatenate((Y, tmp_y), axis=0)
    if sea and night:
        tmp_x, tmp_y = dataset['_sea_n']['x'], dataset['_sea_n']['y']
        X = tmp_x if X is None else np.concatenate((X, tmp_x), axis=0)
        Y = tmp_y if Y is None else np.concatenate((Y, tmp_y), axis=0)
    if land and day:
        tmp_x, tmp_y = dataset['_land_d']['x'], dataset['_land_d']['y']
        X = tmp_x if X is None else np.concatenate((X, tmp_x), axis=0)
        Y = tmp_y if Y is None else np.concatenate((Y, tmp_y), axis=0)
    if land and night:
        tmp_x, tmp_y = dataset['_land_n']['x'], dataset['_land_n']['y']
        X = tmp_x if X is None else np.concatenate((X, tmp_x), axis=0)
        Y = tmp_y if Y is None else np.concatenate((Y, tmp_y), axis=0)

    X, Y = sampling(X, Y)

    Y = Y.ravel()
    print('Datashape after sampling:', X.shape, Y.shape)
    # Normalization
    

    # Split the dataset
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=0)

    scaler = StandardScaler()
    scaler.fit(X_train[:,:-1])
    X_train_trans = scaler.transform(X_train[:,:-1])

    scaler.fit(X_test[:,:-1])
    X_test_trans = scaler.transform(X_test[:,:-1])

    # Init model
    svc = SVC(gamma='auto', tol=1e-5)
    # svc = LinearSVC(tol=1e-5)

    # Train
    print('Training...')
    # svc.fit(X_train_trans, y_train)
    
    # Plot the train result
    print('Plotting...')
    tag_name = ''
    if sea: tag_name += '_sea'
    if land: tag_name += '_land'
    if day: tag_name += '_d'
    if night: tag_name += '_n'
    title = "Seafog" + tag_name

    plt = plot_learning_curve(svc, title, X_train, y_train)
    plt.show()

    # save model
    dataset_path = os.path.join('seafog_svm', 'data', 'output', 'dataset' + tag_name + latlon_range)
    joblib.dump(svc, dataset_path + '.pkl')

    # Predic on test set
    # # clf = joblib.load('seafog_svm\data\output\dataset.pkl')
    y_pred = svc.predict(X_test_trans)

    # result
    # print(mean_squared_error(y_test, y_pred))
    print('Analyzing...')
    get_error_anal(X_test, y_pred, y_test, 'error', tag_name)
    print(classification_report(y_test, y_pred))
    mat = confusion_matrix(y_test, y_pred)
    print(mat)
    # tn, fp, fn, tp = mat.ravel()
    

def predict():
    clf = joblib.load('seafog_svm\data\output\dataset.pkl')


start_time = time.time()
train(area='all', sea=True, land=True, day=True, night=True)
# predict()
print('Total time:' + str(time.time() - start_time))