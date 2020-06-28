import numpy as np
from vfm_row2block import vfm_row2block
from interpret_vfm_type import extract_type, Feature_Type
import cv2
import os.path as osp


def plot_vfm(hdf_file, file_name):
    # 15 profiles are in 1 record of VFM data. At the highest altitudes 5 profiles are averaged
    # together. In the mid altitudes 3 are averaged and at roughly 8 km or less, there are
    # separate profiles.
    prof_per_row = 15
    alt_len = 545

    fcf = hdf_file.select('Feature_Classification_Flags')
    dataset = fcf.get()
    # print(dataset.shape)
    dataset = np.ma.masked_equal(dataset, -999)

    # Give the number of rows in the dataset
    num_rows = dataset.shape[0]

    # Create an empty array the size of of L1 array so they match on the plot
    unpacked_vfm = np.zeros((alt_len, prof_per_row * num_rows), np.uint8)

    # Assign the values from 0-7 to subtype
    vfm = extract_type(dataset)

    # Place 15-wide, alt_len-tall blocks of data into the
    for i in range(num_rows):
        unpacked_vfm[:, prof_per_row * i:prof_per_row *
                     (i + 1)] = vfm_row2block(vfm[i, :])
    vfm = unpacked_vfm

    # print(np.max(vfm), np.min(vfm))

    def gen_fcf_img():
        """
        Extracts feature type for each element in a vertical feature mask array:

            0 = invalid (bad or missing data)  black
            1 = 'clear air'                    red
            2 = cloud                          light blue
            3 = aerosol                        yellow
            4 = stratospheric feature          pink
            5 = surface                        dark blue
            6 = subsurface                     green
            7 = no signal (totally attenuated)
        """
        img = np.zeros((vfm.shape[0], vfm.shape[1], 3), dtype=np.uint8)
        colors = [[0, 0, 0], [0, 0, 255], [220, 220, 0], [0, 220, 220], [220, 0, 220], [255, 0, 0], [0, 255, 0], [0, 0, 0]]
        for i, rows in enumerate(vfm):
            for j, cell in enumerate(rows):
                img[i, j] = colors[cell]
        file_dir = r'calipso\result_data'
        img_name = osp.join(file_dir, file_name[:-3])
        cv2.imwrite(img_name + 'png', img)
        print('File write to ' + img_name + 'png')
        
    gen_fcf_img()
