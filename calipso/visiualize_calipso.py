# visiualize calipso vfm data

import numpy as np
import cv2
import os
from calipso_file import CalipsoFile
from cfg import GenCfg

# https://www-calipso.larc.nasa.gov/resources/calipso_users_guide/data_summaries/vfm/


def read_files(dir_path, plot_single = True):
    img = np.full((GenCfg.SIZE_HEIGHT, GenCfg.SIZE_WIDTH, 3), 255, dtype=np.uint8)
    for fn in os.listdir(dir_path):
        if fn[-4:] == '.hdf' and fn[-12] == 'D':
            calipso_file = CalipsoFile(dir_path, fn)
            calipso_file.plot_vfm(GenCfg.RESULT_PATH)
            img = calipso_file.plot_path(img, GenCfg.FOG_RATIO)

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



# read_files(GenCfg.HDF_FILE_DIR)
# test_file(r"calipso\data\2018", r"CAL_LID_L2_VFM-Standard-V4-20.2018-04-18T04-07-42ZD_Subset.hdf")

