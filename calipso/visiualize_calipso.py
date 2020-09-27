# visiualize calipso vfm data
from PIL import Image
import numpy as np
import cv2
import os
from calipso_file import CalipsoFile
from cfg import GenCfg
from datetime import datetime, timedelta

# https://www-calipso.larc.nasa.gov/resources/calipso_users_guide/data_summaries/vfm/


def read_files(dir_path, plot_single = True):
    img = np.full((GenCfg.SIZE_HEIGHT, GenCfg.SIZE_WIDTH, 3), 255, dtype=np.uint8)
    for fn in os.listdir(dir_path):
        if fn[-4:] == '.hdf' and fn[-12] == 'D':
            calipso_file = CalipsoFile(dir_path, fn)
            calipso_file.plot_vfm(GenCfg.RESULT_PATH)
            img = calipso_file.plot_path_with_mask(img, GenCfg.FOG_RATIO)

            if plot_single:
                cv2.imwrite(r"calipso\\result_data\\path\\"+ fn + ".png", img)
                img = np.full((GenCfg.SIZE_HEIGHT, GenCfg.SIZE_WIDTH, 3), 255, dtype=np.uint8)

    if not plot_single:
        cv2.imwrite(r"calipso\\result_data\\path1.png", img)

def test_file(dir_path, file_name):
    img = np.full((GenCfg.SIZE_HEIGHT, GenCfg.SIZE_WIDTH, 3), 255, dtype=np.uint8)
    calipso_file = CalipsoFile(dir_path, file_name)
    calipso_file.plot_vfm(r"calipso\\result_data")
    fog_mask = calipso_file.get_vfm_fog_mask(GenCfg.FOG_RATIO)
    print(fog_mask.shape)
    print(np.sum(fog_mask))

    img = calipso_file.plot_path(img, GenCfg.FOG_RATIO)
    cv2.imwrite(r"calipso\\result_data\\path4.png", img)


def get_file_dir(path_dic, dt):
    folder_name = dt.strftime('%Y%m%d')
    path = path_dic.get(folder_name)

    if path == None:
        return path

    path = os.path.join(path, dt.strftime('%H%M'))
    return path

def get_path_dic(target_dir):
    dic = {}
    # change target_dir if want to run in another dic
    for main_dir in os.listdir(target_dir):
        for sub_dir in os.listdir(os.path.join(target_dir, main_dir)):
            dic[sub_dir] = os.path.join(target_dir, main_dir , sub_dir)
    return dic

def get_datetime(fn):
    dt_str = fn[30:49]
    dt = datetime.strptime(dt_str, "%Y-%m-%dT%H-%M-%S")
    return dt

def trans_time(dt, threshold):
    minute = dt.minute

    min_dif = min(abs(minute - 0), abs(minute - 30), abs(minute - 60))
    if min_dif > threshold:
        return None
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
    return fn
    if not os.path.exists(fn):
        return
    img = np.asarray(Image.open(fn))
    return img

def get_result_path(result_dir, dt):
    result_path = os.path.join(result_dir, str(dt.year), str(dt.month), str(dt.date), )
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    return result_path

def plot_path_vfm(vfm_dir_path, him_dir_path, result_dir):
    path_dic = get_path_dic(him_dir_path)
    for fn in os.listdir(vfm_dir_path):
        if fn[-4:] == '.hdf':
            vfm_dt = get_datetime(fn)
            him_dt = trans_time(vfm_dt, 10)
            if him_dt == None:
                continue
            file_path = get_file_dir(path_dic, him_dt)
            him_nc_img = get_nc_img(him_dt, file_path)
            if him_nc_img == None:
                continue
            calipso_file = CalipsoFile(vfm_dir_path, fn)

            path_mask = np.full((GenCfg.SIZE_HEIGHT, GenCfg.SIZE_WIDTH, 3), 1, dtype=np.uint8)

            vfm_img = calipso_file.get_plot_vfm()
            path_mask = calipso_file.get_plot_path(path_mask)
            path_img = np.multiply(path_mask, him_nc_img)

            result_path = get_result_path(result_dir, him_dt)
            cv2.imwrite(os.path.join(result_path, "vfm.png"), vfm_img)
            cv2.imwrite(os.path.join(result_path, "path_mask.png"), path_mask)
            cv2.imwrite(os.path.join(result_path, "path_img.png"), path_img)

# read_files(r'calipso\data\2020\202005')
# test_file(r"calipso\data\2018", r"CAL_LID_L2_VFM-Standard-V4-20.2018-04-18T04-07-42ZD_Subset.hdf")
