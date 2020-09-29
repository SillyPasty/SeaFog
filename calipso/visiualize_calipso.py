# visiualize calipso vfm data
from PIL import Image
import numpy as np
import cv2
import os
from calipso_file import CalipsoFile
from cfg import GenCfg
from datetime import datetime, timedelta
import time

# https://www-calipso.larc.nasa.gov/resources/calipso_users_guide/data_summaries/vfm/
SIZE_WIDTH = 3600
SIZE_HEIGHT = 2160

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

def get_result_path(result_dir, dt):
    result_path = os.path.join(result_dir, str(dt.year), '{:02d}'.format(dt.month), '{:02d}'.format(dt.day), '{:02d}{:02d}'.format(dt.hour, dt.minute))
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    return result_path

def plot_path_vfm(vfm_dir_path, path_dic, result_dir):
    total, invalid_vfm, invalid_him = 0, 0, 0
    for fn in os.listdir(vfm_dir_path):
        if fn[-4:] == '.hdf':
            total += 1
            print('\rProcessing {}'.format(fn), end='')
            calipso_file = CalipsoFile(vfm_dir_path, fn)
            if not calipso_file.is_valid_file(10):
                # print('\nCalipso data does not valid!')
                invalid_vfm += 1
                continue
            vfm_dt = calipso_file.get_start_time()
            him_dt = trans_time(vfm_dt)
            file_path = get_file_dir(path_dic, him_dt)
            if file_path == None:
                # print('\nHim data does not exist!')
                invalid_him += 1
                continue
            # him_nc_img = np.asarray(Image.open(file_path))
            him_nc_img, flg = get_nc_img(him_dt, file_path)
            
            if flg == False:
                # print('\nHim image does not exist!')
                invalid_him += 1
                continue

            path_mask = np.full((SIZE_HEIGHT, SIZE_WIDTH, 1), 1, dtype=np.uint8)

            vfm_img = calipso_file.get_plot_vfm()
            path_mask = calipso_file.get_plot_path(path_mask)
            path_img = np.multiply(path_mask, him_nc_img)
            path_img[:, :, [2, 1, 0]] = path_img[:, :, [0, 1, 2]]

            path_mask_img = np.full((SIZE_HEIGHT, SIZE_WIDTH, 3), 255, dtype=np.uint8)
            path_mask_img = np.multiply(path_mask, path_mask_img)

            result_path = get_result_path(result_dir, him_dt)
            fn_prefix = him_dt.strftime("%Y-%m-%d_%H-%M_")
            cv2.imwrite(os.path.join(result_path, fn_prefix + "vfm.png"), vfm_img)
            cv2.imwrite(os.path.join(result_path, fn_prefix + "path_mask.png"), path_mask_img)
            cv2.imwrite(os.path.join(result_path, fn_prefix + "path_img.png"), path_img)
    return total, invalid_vfm, invalid_him

def count_valid():
    VFM_DIR = os.path.join('calipso', 'data', 'data')
    total, valid = 0, 0
    for sub_dir in os.listdir(VFM_DIR):
        # print(type(sub_dir))
        # if sub_dir != '2017' or sub_dir != '2018' or sub_dir != '2019':
        #     continue
        # print(sub_dir)
        vfm_dir = os.path.join(VFM_DIR, sub_dir)
        for fn in os.listdir(vfm_dir):
            calipso_file = CalipsoFile(vfm_dir, fn)
            if calipso_file.is_valid_file(10):
                valid += 1
            total += 1
    print("Total:", total)
    print("valid:", valid)

def main():
    VFM_DIR = os.path.join('calipso', 'data', 'data')
    HIM_DIR = os.path.join('/NAS', 'Himawari8')
    RESULT_DIR = os.path.join('calipso', 'data', 'output')
    total, invalid_vfm, invalid_him = 0, 0, 0
    path_dic = get_path_dic(HIM_DIR)
    for sub_dir in os.listdir(VFM_DIR):
        vfm_dir = os.path.join(VFM_DIR, sub_dir)
        t, iv, ih = plot_path_vfm(vfm_dir, path_dic, RESULT_DIR)
        total += t
        invalid_vfm += iv
        invalid_him += ih
    print('TOTAL_vfm:', total)
    print('Invalid vfm:', invalid_vfm)
    print('Invalid him:', invalid_him) 

start_t = time.time()
main()
# count_valid()
print('\nTOTAL time:', time.time() - start_t)
