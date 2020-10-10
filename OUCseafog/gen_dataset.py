import numpy as np
import os
from datetime import datetime
import config as cfg
from util import him


def get_dt(fn):
    dt = datetime.strptime(fn[:-4], "%Y%m%d%H%M")
    return dt


def get_OUC_file(fn):
    ouc = np.fromfile(fn, dtype=np.float32)
    ouc = ouc.reshape(cfg.OUC.SIZE[0], cfg.OUC.SIZE[1])
    return ouc


def sample(img):
    """ 0 0.0125  0.025  0.0375  0.05  0.0625  0.075  0.0875  0.1
        0         0.02   0.04          0.06    0.08           0.1
    """
    sampled_img = np.zeros((cfg.OUC.SIZE[0], cfg.OUC.SIZE[1]), dtype=img.dtype)
    tmp_img = np.zeros((cfg.OUC.SIZE[0], img.shape[1]), dtype=img.dtype)
    tmp_idx = 0
    for i in range(img.shape[0]):
        if i % 8 == 0 or i % 8 == 2 or i % 8 == 3 or i % 8 == 5 or i % 8 == 6:
            tmp_img[tmp_idx, :] = img[i, :].copy()
            tmp_idx += 1
    tmp_idx = 0
    for i in range(img.shape[1]):
        if i % 8 == 0 or i % 8 == 2 or i % 8 == 3 or i % 8 == 5 or i % 8 == 6:
            sampled_img[:, tmp_idx] = tmp_img[:, i].copy()
            tmp_idx += 1
    return sampled_img


def get_sample_B07_B13(out_fn, path_dic):
    dt = get_dt(ouc_fn[-16:])
    fd = him.get_file_dir(path_dic, dt)
    ouc = get_OUC_file(ouc_fn)
    dataset_list = []
    range = {3, 17}
    for i in range:
        ch_img, flag = him.get_channel_img(dt, fd, i)
        if not flag:
            inv = 1
            continue
        ch_img = him.get_target_area(cfg.OUC.START_LON, cfg.OUC.END_LON, cfg.OUC.START_LAT, cfg.OUC.END_LAT, ch_img)
        ch_img = sample(ch_img)
        dataset_list.append(ch_img)
    dataset_list.append(ouc)
    reslist = []
    for img in dataset_list:
        res = np.array(img)
        reslist.append(res)
    return reslist

def get_simple(ouc_fn, path_dic):
    dt = get_dt(ouc_fn[-16:])
    fd = him.get_file_dir(path_dic, dt)
    ouc = get_OUC_file(ouc_fn)
    dataset_list = []
    for i in range(1, 17):
        ch_img, flag = him.get_channel_img(dt, fd, i)
        if flag == False:
            inv = 1
            continue
        ch_img = him.get_target_area(cfg.OUC.START_LON, cfg.OUC.END_LON, cfg.OUC.START_LAT, cfg.OUC.END_LAT, ch_img)
        ch_img = sample(ch_img)
        dataset_list.append(ch_img)
    dataset_list.append(ouc)
    res = np.array(dataset_list)
    res = res.transpose(1, 2, 0)
    res = res.reshape(-1, 17)
    np.save('test', res)


def stat_data(ouc_fn):
    ouc = np.fromfile(ouc_fn, dtype=np.float32)
    res = count_np(ouc)
    return res


def count_np(arr):
    result = {}
    key = np.unique(arr)
    for k in key:
        mask = (arr == k)
        result[k] = np.sum(mask)
    return result


def merge_dic(x, y):
    for k, v in x.items():
        if k in y.keys():
            y[k] += v
        else:
            y[k] = v
    return y


def main(ouc_dir):
    # path_dic = him.get_path_dic(r'')
    res = {}
    for fn in os.listdir(ouc_dir):
        if fn[-4:] != '.dat':
            continue
        ouc_fn = os.path.join(ouc_dir, fn)
        print('\rProcessing {}'.format(ouc_fn), end='')
        result = stat_data(ouc_fn)
        res = merge_dic(res, result)
    print()
    print(res)


path_dic = him.get_path_dic(r'数据\himexp')
ouc_fn = r'数据\海大反演\参考夜间结果\2019\201903140000.dat'
# get_simple(ouc_fn, path_dic)
main(r'数据\海大反演\参考夜间结果\2020')

# 0.0: 405584026, 1.0: 1288106302, 2.0: 670944089, 3.0: 16461881
# 0.0: 148165206, 1.0: 621138112, 2.0: 257678007, 3.0: 16143758
