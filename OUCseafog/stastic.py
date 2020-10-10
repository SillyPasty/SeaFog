import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import datetime
import os


def filter_mask(channel13, channel7, ouc_mask):
    # 0 sunny, 1 land, 2 cloud, 3 fog
    ouc_mask.astype(np.int32)
    fog_mask = (ouc_mask == 3)
    print(np.sum(fog_mask))
    fog_mask = (ouc_mask != 3)
    
    sub = channel13 - channel7
    sub = np.ma.masked_array(sub, mask = fog_mask)
    
    return sub


def count_values(sub):
    dic = {}
    keys = np.unique(sub)
    for key in keys:
        # print(type(key))
        if type(key) != np.int32:
            continue
        dic[key] = np.sum((sub == key))
    return dic


def plot_pic(out_dic, dic, dt):
    title = dt.strftime('%Y-%m-%d_%H-%M')
    plt.clf()
    plt.bar(dic.keys(), dic.values())
    plt.xlabel('Difference')
    plt.ylabel('number')
    plt.title(title)
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(1))
    fn = os.path.join(out_dic, (title + '_ouc_stat.png'))
    # plt.show()
    plt.savefig(fn)


def anal_ouc(out_dic, dt, ch13, ch7, ouc):
    # print(ch13)
    # print(ch7)
    sub = filter_mask(ch13, ch7, ouc)
    # print(sub)
    dic = count_values(sub)
    print(dic)
    plot_pic(out_dic, dic, dt)
