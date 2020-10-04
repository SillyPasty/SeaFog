import os
import numpy as np
from PIL import Image
from datetime import datetime, timedelta


def get_file_dir(path_dic, dt):
    folder_name = dt.strftime('%Y%m%d')
    path = path_dic.get(folder_name)

    if path == None:
        return path
    # return path
    path = os.path.join(path, dt.strftime('%H%M'))
    return path

def get_path_dic(target_dir):
    dic = {}
    # change target_dir if want to run in another dic
    for main_dir in os.listdir(target_dir):
        if not os.path.isdir(os.path.join(target_dir, main_dir)):
            continue
        for sub_dir in os.listdir(os.path.join(target_dir, main_dir)):
            dic[sub_dir] = os.path.join(target_dir, main_dir , sub_dir)
    return dic

def trans_time(dt):
    minute = dt.minute
    him_datetime = dt
    him_datetime -= timedelta(minutes=dt.minute, seconds=dt.second)

    if minute < 15: 
        pass
    elif minute > 45:
        him_datetime += timedelta(hours=1)
    else:
        him_datetime += timedelta(minutes=30)
    
    return him_datetime

def get_nc_img(dt, file_dir):
    nc_fn = "nc_{}_w3600_h2160.png".format(dt.strftime("%Y%m%d_%H%M"))
    fn = os.path.join(file_dir, nc_fn)
    if not os.path.exists(fn):
        return None, False
    img = np.asarray(Image.open(fn))
    return img, True

def get_channel_img(dt, file_dir, ch):
    gray_fn = "B{:02}_{}.png".format(ch, dt.strftime("%Y%m%d_%H%M"))
    fn = os.path.join(file_dir, gray_fn)
    if not os.path.exists(fn):
        return None, False
    img = np.asarray(Image.open(fn))
    return img, True

def get_target_area(lon_s, lon_e, lat_s, lat_e, img):
    x_s = int((lat_s - 45) / -0.0125)
    x_e = int(x_s + (lat_e - lat_s) / -0.0125)
    y_s = int((lon_s - 105) / 0.0125)
    y_e = int(y_s + (lon_e - lon_s) / 0.0125)
    return img[x_s:x_e+1, y_s:y_e+1]