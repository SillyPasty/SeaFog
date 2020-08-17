# used on the server
# Generate datasets from vfm datasets
# Him + Calipso

import csv
import os
import datetime
import cv2
from PIL import Image
import numpy as np
import time
import math
import joblib

SPACE_R = 0.0125
START_LAT = 45.
START_LON = 105.

def get_axis(lat, lon):
    x_axis = int((START_LAT - float(lat)) / SPACE_R)
    y_axis = int((float(lon) - START_LON) / SPACE_R)
    
    if x_axis == 2160: x_axis -= 1
    if y_axis == 3600: y_axis -= 1

    return x_axis, y_axis

def get_file_dir(path_dic, dt):
    folder_name = dt.strftime('%Y%m%d')
    path = path_dic.get(folder_name)

    if path == None:
        return path

    path = os.path.join(path, dt.strftime('%H%M'))
    return path

def get_path_dic():
    dic = {}
    target_dir = os.path.join('data', 'images') # change if want to run in another dic
    for main_dir in os.listdir(target_dir):
        for sub_dir in os.listdir(os.path.join(target_dir, main_dir)):
            dic[sub_dir] = os.path.join(target_dir, main_dir, sub_dir)
    return dic

def get_him_data(path_dic, him_time):
    him_data = []
    for i in range(1, 17):
        channel_str = 'B{:0>2d}'.format(i)

        him_file_dir = get_file_dir(path_dic, him_time)

        if him_file_dir == None:
            him_data.append(None)
            continue

        him_file_name = channel_str + '_' + him_time.strftime('%Y%m%d_%H%M') + '.png'

        him_file = os.path.join(him_file_dir, him_file_name)

        if os.path.exists(him_file):
            # print('\rReading img ', him_file, end='')
            img = np.asarray(Image.open(him_file))
            him_data.append(img)
        else:
            him_data.append(None)
    # 16 * height * width
    return him_data

def test(model_path, data_path, time_range):
    model = joblib.load(model_path + '.pkl')

    
    

def main():
    start_time = time.time()
    path_dic = get_path_dic()
    vfm_dir = os.path.join('calipso', 'vfm')
    vfm_him_dir = os.path.join('calipso', 'him_vfm')
    stat = {'total': 0, 'success': 0, 'failed': 0}
    for fn in os.listdir(vfm_dir):
        vfm_fn = os.path.join(vfm_dir, fn)
        vfm_him_fn = os.path.join(vfm_him_dir, fn)
        print('Processing ', vfm_fn)

    print('Time cost: ', str(time.time() - start_time))
    print('Total: {total}, Success: {success}, Failed: {failed}'.format(**stat))

main()
