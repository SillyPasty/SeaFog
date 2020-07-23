# Generate calipso dataset
import numpy as np
from calipso_file import CalipsoFile
import datetime
import math
import csv
import os
from cfg import GenCfg

EXAMPLE_FOLDER = r"calipso\data\2017"

def gen_dataset(file_dir, file_name, csv_writer):
    result_dic = {}
    calipso_file = CalipsoFile(file_dir, file_name)

    fog_mask = calipso_file.get_vfm_fog_mask(0.8, 1000)
    land_water_mask = calipso_file.get_land_water_mask()

    ss_time = calipso_file.get_time()
    lon_arr, lat_arr = calipso_file.get_lon_lat()
    LEN = ss_time.shape[0]

    for i in range(LEN-1):
        time = parse_ss_time(ss_time[i][0])
        time -= datetime.timedelta(microseconds=time.microsecond)
        him_time = trans_time(time, 10)
        if him_time == None:
            continue

        him_lonlat, distance = parse_ss_lonlat(lon_arr[i][0], lat_arr[i][0])
        if him_lonlat[0] < 105 or him_lonlat[0] > 150 or \
            him_lonlat[1] < 18 or him_lonlat[1] > 45:
            continue

        temp_dic = {'calipso_time': time, # calipso time
                    'him_time': him_time, # him time
                    'distance': distance, 
                    'fog': fog_mask[i][0], 
                    'lw': land_water_mask[i][0]}

        cur_dic = result_dic.get(him_lonlat)

        result_dic[him_lonlat] = temp_dic if (cur_dic == None or cur_dic['distance'] > distance) else cur_dic
    
    for k, v in result_dic.items():
        items = {'lon':k[0],
                 'lat':k[1],
                 'real_time': v['calipso_time'],
                 'him_time': v['him_time'],
                 'fog_mask': v['fog'],
                 'land_water_mask': v['lw']}
        csv_writer.writerow(items)

def trans_time(dt, threshold):
    minute = dt.minute

    min_dif = min(abs(minute - 0), abs(minute - 30), abs(minute - 60))
    if min_dif > threshold:
        return None
    him_datetime = dt
    him_datetime -= datetime.timedelta(minutes=dt.minute, seconds=dt.second, microseconds=dt.microsecond)

    if minute < 15: 
        pass
    elif minute > 45:
        him_datetime += datetime.timedelta(hours=1)
    else:
        him_datetime += datetime.timedelta(minutes=30)
    
    return him_datetime

def parse_ss_time(ss_time):
    time_str = str(ss_time)
    form = '%y%m%d'
    time = datetime.datetime.strptime(time_str[:6], form)
    fraction = float(time_str[6:])
    delta = datetime.timedelta(seconds = 24 * 3600 * fraction)
    time += delta
    return time

def parse_ss_lonlat(lon, lat):

    cal2him = lambda a: int(a * 10) / 10 + GenCfg.SPACE_R * (int(round((int(a * 10000) % 1000) / 125, 0)))


    him_lon = cal2him(lon)
    him_lat = cal2him(lat)

    distance = math.sqrt((him_lon-lon)**2 + (him_lat-lat)**2)

    return (him_lon, him_lat), distance

def main(dir_path):
    dt = None
    idx = 0
    dir_list = os.listdir(dir_path)
    cur_path = os.path.dirname(__file__)
    while idx < len(dir_list):
        fn = dir_list[idx]

        if dt == None:
            dt = fn[30:37] # init

        csv_fn = os.path.join(cur_path, 'result_data', 'dataset', dt + '.csv')
        print(dt)
        with open(csv_fn, 'wt') as f:
            headers = ['lon', 'lat', 'real_time', 'him_time', 'fog_mask', 'land_water_mask']
            cw = csv.DictWriter(f,fieldnames=headers, lineterminator='\n')
            cw.writeheader()
            while idx < len(dir_list):
                fn = dir_list[idx]

                if fn[30:37] != dt:
                    dt = fn[30:37]
                    break

                gen_dataset(dir_path, fn, cw)
                idx += 1

    return
        

main(EXAMPLE_FOLDER)
