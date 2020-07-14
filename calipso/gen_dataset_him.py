import csv
import os
import datetime
import cv2
from PIL import Image
import numpy as np

SPACE_R = 0.0125
START_LAT = 45.
START_LON = 105.

def get_axis(lat, lon):
    x_axis = (START_LAT - float(lat)) / SPACE_R
    y_axis = (float(lon) - START_LON) / SPACE_R
    return int(x_axis), int(y_axis)

def get_file_dir(path_dic, dt):
    folder_name = dt.strftime('%Y%m%d')
    path = path_dic[folder_name]
    path = os.path.join(path, dt.strftime('%H%M'))
    return path

def get_path_dic():
    dic = {}
    target_dir = os.path.join('data', 'images') # change if want to run in another dic
    for main_dir in os.listdir(target_dir):
        for sub_dir in os.listdir(os.path.join(target_dir, main_dir)):
            dic[sub_dir] = os.path.join(target_dir, main_dir , sub_dir)
    return dic

def gen_him_vfm_dataset(vfm_fn, vfm_him_fn, path_dic):
    with open(vfm_fn, 'r') as vfm_f:
        with open(vfm_him_fn, 'w') as vfm_him_f:
            
            vfm_headers = ['lon', 'lat', 'real_time', 'him_time', 'fog_mask', 'land_water_mask']
            him_headers = ['B' + '{:0>2d}'.format(i) for i in range(1, 17)]
            headers = vfm_headers + him_headers

            reader = csv.DictReader(vfm_f, headers)

            cw = csv.DictWriter(vfm_him_f,fieldnames=headers, lineterminator='\n')
            cw.writeheader()

            for i, row in enumerate(reader):
                if i == 0:
                    continue

                lon, lat = row['lon'], row['lat']
                him_time = datetime.datetime.strptime(row['him_time'], '%Y-%m-%d %H:%M')

                for i in range(1, 17):
                    channel_str = 'B{:0>2d}'.format(i)

                    him_file_dir = get_file_dir(path_dic, him_time)
                    him_file_name = channel_str + '_' + him_time.strftime('%Y%m%d_%H%M') + '.png'
                    him_file = os.path.join(him_file_dir, him_file_name)

                    if os.path.exists(him_file):
                        img = np.asarray(Image.open(him_file))
                        x, y = get_axis(lat, lon)
                        val = img[x, y]

                        if i > 6:
                            val += 200

                        row[channel_str] = val
                    else:
                        row[channel_str] = -1

                cw.writerow(row)

def main():
    path_dic = get_path_dic()
    vfm_dir = os.path.join('calipso', 'vfm')
    vfm_him_dir = os.path.join('calipso', 'him_vfm')
    for fn in os.listdir(vfm_dir):
        vfm_fn = os.path.join(vfm_dir, fn)
        vfm_him_fn = os.path.join(vfm_him_dir, fn)
        gen_him_vfm_dataset(vfm_fn, vfm_him_fn, path_dic)

main()
