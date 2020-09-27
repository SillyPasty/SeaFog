from PIL import Image
import numpy as np

def img_merge(img_dic, gamma_dic):
    """ 
    Input three images (R, G, B) and gamma
    Merge them and return.
    """
    img = None
    return img

def get_fn(channel, dt):
    """ 
    Input channel and datetime
    Return him filename
    """
    if channel == 0:
        return None
    fn = ""
    return fn

def substract(img_a, img_b, ranges):
    """ 
    return A - B within range (tuple)
    """
    maximum, minimum = ranges
    img = None
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
        img_b = np.zeros(img_a.shape) # TODO: add dtype attribute
        if img_b_path != None:
            img_b = np.asarray(Image.open(img_b_path))

        img_dic[ch] = substract(img_a, img_b, range_dic[ch])

    merged_img = img_merge(img_dic, gamma_dic)
    return merged_img