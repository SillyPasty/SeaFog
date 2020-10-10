import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import datetime
import os


def filter_mask(channel13, channel7, ouc_mask):
    # 0 sunny, 1 land, 2 cloud, 3 fog
    ouc_mask.astype(np.int32)
    fog_mask = (ouc_mask == 3)
    ch13_masked = np.multiply(channel13, fog_mask)
    ch7_masked = np.multiply(channel7, fog_mask)
    sub = ch13_masked - ch7_masked
    return sub


def count_values(sub):
    dic = {}
    keys = np.unique(sub)
    for key in keys:
        dic[key] = np.sum((sub == key))
    return dic


def plot_pic(out_dic, dic, dt):
    title = dt.strftime('%Y-%m-%d %H:%M')
    plt.clf()
    plt.bar(dic.keys(), dic.values())
    plt.xlabel('Difference')
    plt.ylabel('number')
    plt.title(title)
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(1))
    fn = os.path.join(out_dic, (title + '_ouc_stat.png'))
    plt.savefig(fn)


def anal_ouc(out_dic, dt, ch13, ch7, ouc):
    sub = filter_mask(ch13, ch7, ouc)
    dic = count_values(sub)
    plot_pic(out_dic, dic, dt)
