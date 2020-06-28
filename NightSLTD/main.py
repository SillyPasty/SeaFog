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

def get_tar_cell(tbb_data, start_lon, start_lat, tar_lonlat):
    t_s_lon, t_s_lat, t_e_lon, t_e_lat = tar_lonlat
    t_s_lon_cell = (int)((t_s_lon - start_lon) / cfg.SPACE_RESOLUTION)
    t_s_lat_cell = (int)((t_s_lat - start_lat) / -cfg.SPACE_RESOLUTION)
    t_e_lon_cell = (int)((t_e_lon - start_lon) / cfg.SPACE_RESOLUTION)
    t_e_lat_cell = (int)((t_e_lat - start_lat) / -cfg.SPACE_RESOLUTION)
    # print(t_s_lon_cell, t_e_lon_cell)
    result = tbb_data[t_s_lat_cell:t_e_lat_cell, t_s_lon_cell:t_e_lon_cell]
    # print(result.shape)
    return result


def sltd_predict(clock):
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
    slice_list, local_slice_list = oper.filter_hisd(cfg.HISD_DATA_SOURCE, cfg.HISD_LOCAL_HISD_ROOT, clock)
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
    sltd_mask = ((-5.5 <= sltd) & (sltd <= -2.50))
    # predict
    img = np.zeros((cfg.SIZE_HEIGHT, cfg.SIZE_WIDTH), dtype=np.uint8)
    img += 255
    img = np.multiply(img ,sltd_mask)

    cv2.imwrite(osp.join(cfg.RESULT_FOLDER_PATH, clock + "result.png"), img)
    # cv2.imshow("233", img)
    # cv2.waitKey(0)

def main():
    clock_list = ['1500']
    for clock in clock_list:
        sltd_predict(clock)

main()