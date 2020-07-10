import numpy as np
from . import vfm_row2block
from . import interpret_vfm_type

def get_vfm(hdf_file):
    # 15 profiles are in 1 record of VFM data. At the highest altitudes 5 profiles are averaged
    # together. In the mid altitudes 3 are averaged and at roughly 8 km or less, there are
    # separate profiles.
    prof_per_row = 15
    alt_len = 545

    dataset = hdf_file.select('Feature_Classification_Flags').get()
    # print(dataset.shape)
    dataset = np.ma.masked_equal(dataset, -999)

    # Give the number of rows in the dataset
    num_rows = dataset.shape[0]

    # Create an empty array the size of of L1 array so they match on the plot
    unpacked_vfm = np.zeros((alt_len, prof_per_row * num_rows), np.uint8)

    # Assign the values from 0-7 to subtype
    vfm = interpret_vfm_type.extract_type(dataset)

    # Place 15-wide, alt_len-tall blocks of data into the
    for i in range(num_rows):
        unpacked_vfm[:, prof_per_row * i:prof_per_row * (i + 1)] = vfm_row2block.vfm_row2block(vfm[i, :])
    vfm = unpacked_vfm

    return vfm