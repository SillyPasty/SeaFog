import os
import sys
import numpy as np
import time

from dataset import Dataset
from utils.anal_error import get_error_anal
from utils.get_params import get_params

from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
import joblib

MAIN_PATH = ''
MODEL_PATH = os.path.join(MAIN_PATH, 'model')
DATA_PATH = os.path.join(MAIN_PATH, 'data')
OUTPUT_PATH = os.path.join(MAIN_PATH, 'output')

def get_name_tag(range_dic, sldn_dic):
    tag_name = ''
    if sldn_dic['sea']:
        tag_name += '_sea'
    if sldn_dic['land']:
        tag_name += '_land'
    if sldn_dic['night']:
        tag_name += '_d'
    if sldn_dic['day']:
        tag_name += '_n'
    latlon_range = '_{}_{}_{}_{}'.format(range_dic['lat1'], range_dic['lon1'], range_dic['lat2'], range_dic['lon2'])
    tag_name += latlon_range
    return tag_name

def train(data_path, range_dic, sldn_dic):
    # Get dataset
    dataset = Dataset(data_path, range_dic)
    X, Y = dataset.get_dataset(sldn_dic)
    X, Y = dataset.pn_sampling(X, Y, ratio=1)
    Y = Y.ravel()
    dataset.analysis(X, Y)

    # Split and normalization
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
    # X_test, X_valid, y_test, y_valid = train_test_split(X_test, y_test, test_size=0.33, random_state=0)
    
    scaler = StandardScaler()
    scaler.fit(X_train[:, :-1])
    X_train_trans = scaler.transform(X_train[:, :-1])

    scaler.fit(X_test[:, :-1])
    X_test_trans = scaler.transform(X_test[:, :-1])
    # Init model
    model = SVC(kernel='rbf', probability=True)
    # Grid search  
    best_parameters = grid_s(model, X_train, y_train)
    # Train   
    model = SVC(kernel='rbf', C=best_parameters['C'], gamma=best_parameters['gamma'], probability=True)    
    model.fit(X_train, y_train)

    tag = get_name_tag(range_dic, sldn_dic)
    model_path = os.path.join(MODEL_PATH, 'seafog' + tag)
    joblib.dump(model, model_path + '.pkl')
    print('Model save to:' + model_path + '.pkl')

    test(model_path, X_test, y_test, tag)

    return model

def grid_s(model, X_train, y_train):
    param_grid = {'C': [1e-3, 1e-2, 1e-1, 1, 10, 100, 1000], 'gamma': [1e-3, 1e-2, 1e-1, 0.5, 1]}
    grid_search = GridSearchCV(model, param_grid, n_jobs = 8, verbose=True)    
    grid_search.fit(X_train, y_train)    
    best_parameters = grid_search.best_estimator_.get_params()
    
    for para, val in list(best_parameters.items()):    
        print(para, val)
    return best_parameters

def test(model_path, X, y ,tag):
    model = joblib.load(model_path + '.pkl')
    y_pred = model.predict(X)
    print(classification_report(y, y_pred))
    mat = confusion_matrix(y, y_pred)
    print(mat)
    tn, fp, fn, tp = mat.ravel()
    p = tp / (tp+fp)
    r = tp / (tp+fn)
    f1 = (2*p*r) / (p+r)
    print('Recall: {}, Precision: {}, F1 score: {}.'.format(r, p, f1))

    error_path = os.path.join(OUTPUT_PATH, 'error')
    get_error_anal(X, y_pred, y, error_path, tag)

def main():
    params_fp = os.path.join(MAIN_PATH, 'parameters.csv')
    range_list, sldn_list = get_params(params_fp)
    time_start = time.time()
    time_mid = time.time()
    for range_dic, sldn_dic in zip(range_list, sldn_list):
        model = train(DATA_PATH, range_dic, sldn_dic)
        print('For model:')
        print(range_dic, sldn_dic)
        print('Time cost:' + str(time.time() - time_mid))
        time_mid = time_mid
        print('-------------------------\n')
    time_end = time.time()
    print('Total_time:' + str(time_end - time_start))

saved_std_out = sys.stdout
with open(os.path.join(OUTPUT_PATH, 'out.txt'), 'w+') as f:
    sys.stdout = f  #标准输出重定向至文件
    main()
sys.stdout = saved_std_out