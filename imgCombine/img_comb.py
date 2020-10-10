from PIL import Image
import numpy as np
import os.path as osp
import os
import cv2
import math
from skimage import exposure

"""
def gamma_trans(img,img_gray):
    mean = np.mean(img_gray)
    gamma_val = math.log10(0.5) / math.log10(mean / 255)
    gamma_table = [np.power(x / 255.0, gamma_val) * 255.0 for x in range(256)]
    gamma_table = np.round(np.array(gamma_table)).astype(np.uint8)
    return cv2.LUT(img, gamma_table)
"""


def img_merge(img_dic, gamma_dic):
    """
    Input three images (R, G, B) and gamma
    Merge them and return.
    """
    rgb = []
    for key in img_dic:
        rgb.append(img_dic[key])
    gamma = []
    for key in gamma_dic:
        gamma.append(gamma_dic[key])
    # gamma变换
    gamma_img_r = exposure.adjust_gamma(rgb[0], float(gamma[0]))
    gamma_img_g = exposure.adjust_gamma(rgb[1], float(gamma[1]))
    gamma_img_b = exposure.adjust_gamma(rgb[2], float(gamma[2]))
    img = cv2.merge([gamma_img_r, gamma_img_g, gamma_img_b])

    # img = cv2.merge([rgb[0], rgb[1], rgb[2]])
    return img


def get_fn(channel, dt):
    """
    Input channel and datetime
    Return him filename
    """

    if channel == '0':
        return None
    dir = os.getcwd()
    fn = channel + "_" + dt[0:8] + "_" + dt[8:] + ".png"
    return osp.join(dir, fn)


def recover_orgin_data(img, channel):
    if channel == '0':
        return img
    log_root = math.log(0.0223, 10)
    denom = (1 - log_root) * 0.75

    bandNo = int(channel[1:])
    if bandNo in range(1, 7):
        img = img * denom / 255
        img_temp = img.tolist()
        for i in range(len(img_temp)):
            img_temp[i] = np.power(10, img_temp[i])
        img = np.array(img_temp)
        img = (img + log_root) * 255
    return img


def substract(img_a, img_b, ranges, channels):
    """
    return A - B with range (tuple)
    """
    maximum, minimum = ranges

    img_a.astype(np.uint32)
    img_b.astype(np.uint32)
    img_a = recover_orgin_data(img_a, channels[0])
    img_b = recover_orgin_data(img_b, channels[1])
    img = img_a - img_b
    # 映射到0-255
    img = cv2.normalize(img, None, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC3)
    return img


def input_pros():
    channels = ['R', 'G', 'B']
    channel_dic, gamma_dic, range_dic = {}, {}, {}
    for i in range(3):
        # Input zero means single channel
        # i.e. only use B06 as blue channel
        ch = channels[i]
        print(ch + " Channel")
        channel_a = eval(input("Please input the first channel:"))
        channel_b = eval(input("Please input the second channel:"))
        maximum = eval(input("Please input the maximum of range:"))
        minimum = eval(input("Please input the minimum of range:"))
        gamma = eval(input("Please input the gamma of {} channel:").format(ch))

        channel_dic[ch] = (channel_a, channel_b)
        gamma_dic[ch] = gamma
        range_dic[ch] = (maximum, minimum)
    return channel_dic, gamma_dic, range_dic


def single_pros(dt, channel_dic, gamma_dic, range_dic):
    """
        Input datetime, process input and return
    """
    channels = ['R', 'G', 'B']
    img_dic = {}
    for i in range(3):
        ch = channels[i]

        img_a_path = get_fn(channel_dic[ch][0], dt)
        img_b_path = get_fn(channel_dic[ch][1], dt)

        img_a = np.asarray(Image.open(img_a_path))
        img_b = np.zeros(img_a.shape)  # TODO: add dtype attribute
        if img_b_path != None:
            img_b = np.asarray(Image.open(img_b_path))
        img_dic[ch] = substract(img_a, img_b, range_dic[ch], channel_dic[ch])

    merged_img = img_merge(img_dic, gamma_dic)
    return merged_img


def main():
    # dt is datetime of the him-data
    dt = "201812030330"
    channel_dic, gamma_dic, range_dic = input_pros()
    merged_img = single_pros(dt, channel_dic, gamma_dic, range_dic)
    cv2.imwrite('merged2.png', merged_img)
    cv2.imshow('merged_img', merged_img)
    cv2.waitKey(0)
    # save img


if __name__ == '__main__':
    main()
