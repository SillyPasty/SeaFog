from datetime import datetime
import os
import csv

def anal_error_data(test_X, predicted_Y, test_Y):
    error_list = []
    for i, single_X in enumerate(test_X):
        if predicted_Y[i] == test_Y[i]:
            continue
        timestamp = single_X[-2]
        dt = datetime.fromtimestamp(timestamp)
        hour, minute = dt.hour, dt.minute
        if minute < 15: 
            minute = 0
        elif minute > 45:
            minute = 0
            hour = (hour + 1) % 24
        else:
            minute = 30
        clock = '{:0>2d}:{:0>2d}'.format(hour, minute)
        sl_flag = single_X[-1]
        error_dic = {'sl_flag': sl_flag, 'clock': clock, 'month': dt.month, 'fog_flag': test_Y[i]}
        error_list.append(error_dic)
    return error_list

def save_error(error_list, file_path, tag):
    analysis_path = file_path + tag + '.csv'
    with open(analysis_path, 'w') as f:

        headers = ['month', 'clock', 'sl_flag', 'fog_flag']
        cw = csv.DictWriter(f ,fieldnames=headers, lineterminator='\n')
        cw.writeheader()

        for error in error_list:
            cw.writerow(error)
    print('Error analysis write to:' + analysis_path)

def get_error_anal(test_X, predicted_Y, test_Y, file_path, tag):
    error_list = anal_error_data(test_X, predicted_Y, test_Y)
    save_error(error_list, file_path, tag)
