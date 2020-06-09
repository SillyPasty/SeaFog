import cv2
import config as cfg
import os.path as osp
import os
import numpy as np
import subprocess
import file_operation as oper
from tbb_file import TBBFile

def make_tbb_file(src_list, dst_list):
    ltlat = '45'
    ltlon = '105'
    for i in range(len(cfg.TARGET_CHANNEL)):
        subprocess.run(
            [cfg.HISD2PNG, src_list[i][0], src_list[i][1], src_list[i][2], dst_list[i], ltlat, ltlon]
        )


def sltd_predict():
    """ Make the prediction of seafog with SLTD (For one file)
    
    Using the brightness temperature difference between channel 7 and channel 13.

    1. Get original the file list
    2. Get the tbb data from the original file, 
        using C++ interface, 
        save as xxx.txt.
    3. Apply sltd algorithm and generate mask.
    4. Save the result.

     """
    # Get file list
    slice_list, local_slice_list = oper.filter_hisd(cfg.HISD_DATA_SOURCE, cfg.HISD_LOCAL_HISD_ROOT, 0)
    oper.select_hisd_slice(slice_list, local_slice_list)
    result_list = oper.filter_result()
    # Read data
    make_tbb_file(local_slice_list, result_list)

    s_wave = TBBFile(result_list[0]) # ch 7
    l_wave  = TBBFile(result_list[1]) # ch 13

    if s_wave.channel != 'B07' or l_wave.channel != 'B13':
        print('Wrong channel!')
        exit(0)
    # Generating mask

    # calculate sltd
    sltd = s_wave.tbb_data - l_wave.tbb_data
    # gen mask
    sltd_mask = ((-5.5 <= sltd) & (sltd <= -2.5))
    # predict
    img = np.zeros((cfg.SIZE_HEIGHT, cfg.SIZE_WIDTH), dtype=np.uint8)
    img += 255
    img = np.multiply(img ,sltd_mask)


    cv2.imwrite(osp.join(cfg.RESULT_FOLDER_PATH, "result.png"), img)
    # cv2.imshow("233", img)
    # cv2.waitKey(0)

sltd_predict()