from datetime import datetime
from pytz import timezone
import os
import csv

def anal_error_data(test_X, predicted_Y, test_Y, info_dic):
    error_list = []
    for i, single_X in enumerate(test_X):
        if predicted_Y[i] == test_Y[i]:
            continue
        info_key = single_X[-1]
        info_headers = ['lon', 'lat', 'him_time', 'fog_mask', 'land_water_mask']
        info = info_dic[info_key]
        error_dic = {}
        for idx, header in enumerate(info_headers):
            error_dic[header] = info[idx]
        error_list.append(error_dic)
    return error_list

def save_error(error_list, file_path, tag):
    analysis_path = file_path + tag + '.csv'
    with open(analysis_path, 'w') as f:
        headers = ['lon', 'lat', 'him_time', 'fog_mask', 'land_water_mask']
        cw = csv.DictWriter(f ,fieldnames=headers, lineterminator='\n')
        cw.writeheader()

        for error in error_list:
            cw.writerow(error)
    print('Error analysis write to:' + analysis_path)

def get_error_anal(test_X, predicted_Y, test_Y, file_path, tag, info_dic):
    error_list = anal_error_data(test_X, predicted_Y, test_Y, info_dic)
    save_error(error_list, file_path, tag)
