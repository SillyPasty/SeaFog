from pyhdf.SD import SD
import numpy as np
import cv2
import os
import os.path as osp
from plot_vfm import plot_vfm
from plot_path import get_single_path, get_spacecraft_position

# https://www-calipso.larc.nasa.gov/resources/calipso_users_guide/data_summaries/vfm/

HDF_FILE_DIR = r"calipso\data\202001"
HDF_FILE1 = r"calipso\CAL_LID_L2_VFM-Standard-V4-20.2018-05-14T04-46-55ZD_Subset.hdf"
HDF_FILE2 = r"calipso\data\202002\CAL_LID_L2_VFM-Standard-V4-20.2020-02-02T18-33-15ZN_Subset.hdf"
SIZE_WIDTH = 3602
SIZE_HEIGHT = 2162
def read_general_info(hdf_file):
    datasets_dic = hdf_file.datasets()
    for idx,sds in enumerate(datasets_dic.keys()):
        print(idx, sds)

def read_files(dir_path):
    img = np.zeros((SIZE_HEIGHT, SIZE_WIDTH), dtype=np.uint8)
    for fn in os.listdir(dir_path):
        if fn[-4:] == '.hdf' and fn[-12] == 'N':
            hdf_file = SD(osp.join(dir_path, fn))
            # read_general_info(hdf_file)
            img = get_single_path(hdf_file, img)
            # plot_vfm(hdf_file, fn)
    cv2.imwrite(r"calipso\path.png", img)

def test_file(file_path):
    img = np.zeros((SIZE_HEIGHT, SIZE_WIDTH), dtype=np.uint8)
    hdf_file = SD(file_path)
    # read_general_info(hdf_file)
    img = get_single_path(hdf_file, img)
    # get_spacecraft_position(hdf_file)


read_files(HDF_FILE_DIR)
# test_file(HDF_FILE1)
# test_file(HDF_FILE2)