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
import pysolar
import pytz

SPACE_R = 0.0125
START_LAT = 45.
START_LON = 105.

def get_axis(lat, lon):
    x_axis = int((START_LAT - float(lat)) / SPACE_R)
    y_axis = int((float(lon) - START_LON) / SPACE_R)
    
    if x_axis == 2160: x_axis -= 1
    if y_axis == 3600: y_axis -= 1

    return x_axis, y_axis

def get_solar_angle(datetime, shape):
    solar_angle_data = np.zeros((shape[0], shape[1], 1))
    for i in range(shape[0]):
        for j in range(shape[1]):
            lat = START_LAT - SPACE_R * i
            lon = START_LON + SPACE_R * j
            solar_angle = solar.get_altitude(lat, lon, datetime)
            solar_angle_data[i][j][0] = solar_angle
    return solar_angle_data

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
    him_data = np.asarray(him_data)
    him_data = him_data.transpose(1, 2, 0)
    assert him_data.shape == (2160, 3600, 16), print(him_data.shape)
    return him_data

def plot_mask(origin_map_path, mask, target_area, save_path):
    x_axis1, y_axis1 = get_axis(target_area['lat1'], target_area['lon1'])
    x, y = mask.shape[0], mask.shape[1]
    real_img = cv2.imread(origin_map_path)
    for i in range(x):
        for j in range(y):
            if mask[i, j, 0] == 0:
                continue
            real_img[x_axis1+i, y_axis1+j, 2] = 255
            real_img[x_axis1+i, y_axis1+j, 1] = 255
            real_img[x_axis1+i, y_axis1+j, 0] = 255

    cv2.imwrite(save_path + '.png', real_img)


def test(model_path, data_path, datetime, target_area):
    him_data = get_him_data(data_path, datetime)
    solar_angle = get_solar_angle(datetime, him_data.shape)
    test_data = np.concatenate((him_data, solar_angle), axis=2)
    assert test_data.shape == (2160, 3600, 17), print(test_data.shape)

    x_axis1, y_axis1 = get_axis(target_area['lat1'], target_area['lon1'])
    x_axis2, y_axis2 = get_axis(target_area['lat2'], target_area['lon2'])
    test_data = test_data[x_axis1:x_axis2, y_axis1: y_axis2, :]
    origin_shape = (test_data.shape[0], test_data.shape[1])
    test_data = test_data.reshape(-1, 17)
    
    model = joblib.load(model_path + '.pkl')
    predicted = model.predic(test_data)

    predict_mask = predicted.reshape(origin_shape[0], origin_shape[1], -1)
    return predict_mask

    
    

def main():
    start_time = time.time()
    path_dic = get_path_dic()
    model_path = ''
    output_path = os.path.join('calipso', 'predicted')
    origin_map_path = ''
    target_area = {
        'lat1':1,
        'lon1':2,
        'lat1':3,
        'lat2':4
    }
    time_range = {
        'year': [2019],
        'month': [i for i in range(1, 13)],
        'day': [i for i in range(1, 32)],
        'hour': [i for i in range(24)],
        'minutes': [0, 30]
    }
    for year in time_range['year']:
        for month in time_range['month']:
            for day in time_range['day']:
                for hour in time_range['hour']:
                    for minute in time_range['minutes']:
                        dt = None
                        try:
                            dt = datetime.datetime(year=year, month=month, day=day,hour=hour, minute=minute)
                        except Exception as e:
                            continue
                        file_dir = get_file_dir(path_dic, dt)
                        if file_dir == None:
                            continue
                        mask = test(model_path, file_dir, dt, target_area)
                        
                        result_path = os.path.join(output_path, dt.strftime('%Y-%m-%d %H:%M'))
                        plot_mask(origin_map_path, mask, target_area,  )


    print('Time cost: ', str(time.time() - start_time))

main()
