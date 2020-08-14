import os
import numpy as np
import time
import csv
import config as cfg
from utils.get_params import get_params
from datetime import datetime
from pytz import timezone
import cv2

import matplotlib.pyplot as plt

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

def get_error_data(error_path):
    info_headers = ['lon', 'lat', 'him_time', 'fog_mask', 'land_water_mask', 'error']
    result = []
    with open(error_path, 'r') as f:
        reader = csv.DictReader(f, info_headers)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            result.append(row)
    return result

def plot_error(fig_path, error_infos):
    if not os.path.exists(fig_path):
        os.mkdir(fig_path)
    total = {'month_list': [0 for i in range(12)], 'time_list': [0 for i in range(48)]}
    error = {'month_list': [0 for i in range(12)], 'time_list': [0 for i in range(48)], 'lat':[], 'lon': []}
    for error_info in error_infos:
        dt = datetime.strptime(error_info['him_time'], '%Y-%m-%d %H:%M:%S').replace(tzinfo = timezone('UTC'))
        total['month_list'][dt.month - 1] += 1
        total['time_list'][int(dt.hour * 2 + dt.minute / 30)] += 1
        if error_info['error'] == '1':
            error['month_list'][dt.month - 1] += 1
            error['time_list'][int(dt.hour * 2 + dt.minute / 30) - 1] += 1
            error['lat'].append(error_info['lat'])
            error['lon'].append(error_info['lon'])
    
    total_width, n = 0.8, 3
    width = total_width / n
    # Plot time
    plt_time = plt.subplot(3, 1, 1)
    x_axis = [i for i in range(1, 49)]
    x_axis_labels = ['{}:{:0>2d}'.format(i//2, 30 if (i % 2 == 1) else 0) if (i % 4 == 0) else '' for i in range(48)]
    plt_time.bar(x_axis, error['time_list'], width=width, label='error', fc='y')
    x_axis = [x + width for x in x_axis]
    plt_time.bar(x_axis, total['time_list'], width=width, label='total', fc='r', tick_label=x_axis_labels)
    # plt_time.legend()
    # plt_time.xticks(rotation=270)
    # Plot month
    plt_month = plt.subplot(3, 1, 2)
    x_axis = [i for i in range(1, 13)]
    plt_month.bar(x_axis, error['month_list'], width=width, label='error', fc='y')
    x_axis = [x + width for x in x_axis]
    plt_month.bar(x_axis, total['month_list'], width=width, label='total', fc='r')
    # plt_month.legend()

    plt.savefig(os.path.join(fig_path, 'time.png'))

    # Plot error point on the map
    img_path = os.path.join(cfg.DATA_PATH, 'img', 'area.png')
    real_img = cv2.imread(img_path)
    SPACE_R = 0.025
    SIZE = 1080
    LON_START, LAT_START = 105, 45
    for la, lo in zip(error['lat'], error['lon']):
        y = int((float(lo) - LON_START) / SPACE_R)
        x = int((LAT_START - float(la)) / SPACE_R)
        real_img[x, y, 2] = 255
        real_img[x, y, 1] = 0
        real_img[x, y, 0] = 0
    cv2.imwrite(os.path.join(fig_path, 'map.png'), real_img)
    return


def main():
    params_fp = os.path.join(cfg.MAIN_PATH, cfg.DATA_PREFIX + 'parameters.csv')
    range_list, sldn_list = get_params(params_fp)
    time_start = time.time()
    time_mid = time.time()
    for range_dic, sldn_dic in zip(range_list, sldn_list):
        name_tag = get_name_tag(range_dic, sldn_dic)
        error_file_name = os.path.join(cfg.OUTPUT_PATH, cfg.DATA_PREFIX + 'error' + name_tag + '.csv')
        error = get_error_data(error_file_name)
        
        fig_path = os.path.join(cfg.OUTPUT_PATH, cfg.DATA_PREFIX + 'error' + name_tag)
        plot_error(fig_path, error)
        print('For model:')
        print(range_dic, sldn_dic)
        print('Time cost:' + str(time.time() - time_mid))
        time_mid = time.time()
        print('-------------------------\n')
    time_end = time.time()
    print('Total_time:' + str(time_end - time_start))

main()
