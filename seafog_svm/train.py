import os
import sys
import numpy as np
import time
from datetime import datetime
from pytz import timezone

from dataset import Dataset
from utils.anal_error import get_error_anal
from utils.get_params import get_params
import config as cfg

from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
import joblib




def get_name_tag(range_dic, sldn_dic):
    tag_name = ''
    if sldn_dic['sea']:
        tag_name += '_sea'
    if sldn_dic['land']:
        tag_name += '_land'
    if sldn_dic['night']:
        tag_name += '_n'
    if sldn_dic['day']:
        tag_name += '_d'
    latlon_range = '_{}_{}_{}_{}'.format(range_dic['lat1'], range_dic['lon1'], range_dic['lat2'], range_dic['lon2'])
    tag_name += latlon_range
    return tag_name

def train(data_path, range_dic, sldn_dic):
    # Get dataset
    dataset = Dataset(data_path, range_dic, cfg.DATA_PREFIX)
    X, Y = dataset.get_dataset(sldn_dic)
    X, Y = dataset.pn_sampling(X, Y, ratio=1)
    Y = Y.ravel()
    dataset.analysis(X, Y)

    # Split and normalization
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
    # X_test, X_valid, y_test, y_valid = train_test_split(X_test, y_test, test_size=0.33, random_state=0)
    scaler = StandardScaler()
    remain_idx = -1
    X_train_trans = X_train[:, :remain_idx]
    X_test_trans = X_test[:, :remain_idx]
    scaler.fit(X_train_trans)
    X_train_trans = scaler.transform(X_train_trans)

    scaler.fit(X_test_trans)
    X_test_trans = scaler.transform(X_test_trans)
    print('Features: {}'.format(X_train_trans.shape[1]))
    # Init model
    model = SVC(kernel='rbf', probability=True)
    # Grid search  
    best_parameters = grid_s(model, X_train_trans, y_train)
    # Train   
    # best_parameters = {'C':100, 'gamma': 0.5}
    model = SVC(kernel='rbf', C=best_parameters['C'], gamma=best_parameters['gamma'], tol=0.0001, probability=True)    
    model.fit(X_train_trans, y_train)

    tag = get_name_tag(range_dic, sldn_dic)
    model_path = os.path.join(cfg.MODEL_PATH, cfg.DATA_PREFIX + 'seafog' + tag)
    joblib.dump(model, model_path + '.pkl')
    print('Model save to:' + model_path + '.pkl')
    # Get train result
    test(model_path, X_train_trans, X_train, y_train)
    # Get test result
    y_pred = test(model_path, X_test_trans, X_test, y_test)
    # Get error anal
    info_dic = dataset.get_info_dic()
    error_path = os.path.join(cfg.OUTPUT_PATH, cfg.DATA_PREFIX + 'error')
    get_error_anal(X_test, y_pred, y_test, error_path, tag, info_dic)

    return model

def grid_s(model, X_train, y_train):
    param_grid = {'C': [1e-3, 1e-2, 1e-1, 1, 1e1, 1e2, 1e3, 1e4], 'gamma': [1e-3, 1e-2, 1e-1, 0.5, 1, 3.2, 6.4]}
    grid_search = GridSearchCV(model, param_grid, n_jobs = 4, verbose=True)    
    grid_search.fit(X_train, y_train)    
    best_parameters = grid_search.best_estimator_.get_params()
    
    for para, val in list(best_parameters.items()):    
        print(para, val)
    return best_parameters

def test(model_path, X, X_orig, y):
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
    return y_pred

def main():
    params_fp = os.path.join(cfg.MAIN_PATH, cfg.DATA_PREFIX + 'parameters.csv')
    range_list, sldn_list = get_params(params_fp)
    time_start = time.time()
    time_mid = time.time()
    for range_dic, sldn_dic in zip(range_list, sldn_list):
        model = train(cfg.DATA_PATH, range_dic, sldn_dic)
        print('For model:')
        print(range_dic, sldn_dic)
        print('Time cost:' + str(time.time() - time_mid))
        time_mid = time.time()
        print('-------------------------\n')
    time_end = time.time()
    print('Total_time:' + str(time_end - time_start))

saved_std_out = sys.stdout
with open(os.path.join(cfg.OUTPUT_PATH, cfg.DATA_PREFIX + 'out.txt'), 'w+') as f:
    sys.stdout = f 
    main()
sys.stdout = saved_std_out