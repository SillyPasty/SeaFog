from datetime import datetime
from pytz import timezone
import os
import csv

def anal_error_data(test_X, predicted_Y, test_Y, info_dic):
    error_list = []
    for i, single_X in enumerate(test_X):
        info_key = single_X[-1]
        info_headers = ['lon', 'lat', 'real_time', 'him_time', 'fog_mask', 'land_water_mask']
        him_headers = ['B' + '{:0>2d}'.format(i) for i in range(1, 17)]
        info_headers = info_headers + him_headers
        info = info_dic[info_key]
        error_dic = {}
        for idx, header in enumerate(info_headers):
            error_dic[header] = info[idx]
        error_dic['error'] = 0 if predicted_Y[i] == test_Y[i] else 1
        error_list.append(error_dic)
    return error_list

def save_error(error_list, file_path, tag):
    analysis_path = file_path + tag + '.csv'
    with open(analysis_path, 'w') as f:
        info_headers = ['lon', 'lat', 'real_time', 'him_time', 'fog_mask', 'land_water_mask', 'error']
        him_headers = ['B' + '{:0>2d}'.format(i) for i in range(1, 17)]
        headers = info_headers + him_headers
        cw = csv.DictWriter(f ,fieldnames=headers, lineterminator='\n')
        cw.writeheader()

        for error in error_list:
            cw.writerow(error)
    print('Error analysis write to:' + analysis_path)

def get_error_anal(test_X, predicted_Y, test_Y, file_path, tag, info_dic):
    error_list = anal_error_data(test_X, predicted_Y, test_Y, info_dic)
    save_error(error_list, file_path, tag)
