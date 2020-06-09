import numpy as np
import cv2
import os
import os.path as osp
import config as cfg

def gen_image(real_img_path ,sTT_file, area_data):
    """ Generate the merged image of stt file and original image.

    1. Visualize the stt data.
    2. Merge the file
    3. Save file.

    Args:
        real_img_path: The original image's path.
        sTT_file: The STT file object.
        area_data: The target area data.
        
    """
    date, time = sTT_file.get_datetime()
    file_name = "{}-{}.png".format(date, time)

    sTT_img_data = np.zeros((area_data.shape[0], area_data.shape[1], 3), dtype=np.uint8)

    # Visiualization of the stt.
    sTT_img_data[:,:,1] = sTT_img_data[:,:,1] + norm(sTT_file, area_data) * 0.4
    sTT_img_data[:,:,2] = sTT_img_data[:,:,2] + norm(sTT_file, area_data)

    # Because the difference of the spacial resolution, resize the image.
    sTT_img = cv2.resize(sTT_img_data, (cfg.SIZE, cfg.SIZE), interpolation=cv2.INTER_NEAREST)
    real_img = cv2.imread(real_img_path)
    result_img = cv2.addWeighted(real_img, 1, sTT_img, 0.4, 0)

    if not osp.exists(cfg.RESULT_FOLDER_PATH):
        os.makedirs(cfg.RESULT_FOLDER_PATH)

    # Save img or show img
    # cv2.imwrite(osp.join(cfg.RESULT_FOLDER_PATH, file_name), sTT_img)
    cv2.imshow(file_name, result_img)
    cv2.waitKey(0)


def norm(sTT_file, data):
    """ Normalize the tem data.
    With mean = 255 / 2
    In range 0, 255.
    """
    variance = np.var(data)
    mean = np.mean(data)
    data = (data - mean) / variance
    data = (data + 0.5) * 255
    data = np.array(data, dtype=np.uint8)
    
    return data
