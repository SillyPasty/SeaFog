import os
import os.path as osp
import bz2
import shutil
import config as cfg

def filter_hisd(dst_dir, local_dir, clock):
    """ Get the original and the extracted file path.

    Get the specific slices. e.g. "S0210"
    Only get channel 7 and 13 !

    Args:
        dst_dir: The original data folder
        local_dir: The extracted data folder
        clock: TODO
    
    Returns:
        Two 2-dim lists, size of (number of slices, number of channel)
    """

    # extract hisd-files into local dir ./data/local_slice
    slice_num = 3
    slice_list = [[None for i in range(slice_num)] for row in range(2)]
    local_slice_list = [[None for i in range(slice_num)] for row in range(2)]
    row_index = 0
    for fn in os.listdir(dst_dir):
        if cfg.TARGET_CHANNEL.count(fn[21:24]) > 0:
            if fn.find("S0210") != -1:
                slice_list[row_index][0] = osp.join(dst_dir, fn)
                local_fn = fn.strip(".bz2")
                local_slice_list[row_index][0] = osp.join(local_dir, local_fn)
            elif fn.find("S0310") != -1:
                slice_list[row_index][1] = osp.join(dst_dir, fn)
                local_fn = fn.strip(".bz2")
                local_slice_list[row_index][1] = osp.join(local_dir, local_fn)
            elif fn.find("S0410") != -1:
                slice_list[row_index][2] = osp.join(dst_dir, fn)
                local_fn = fn.strip(".bz2")
                local_slice_list[row_index][2] = osp.join(local_dir, local_fn)
                row_index += 1

    return slice_list, local_slice_list

def filter_result():
    res = []
    for ch in cfg.TARGET_CHANNEL:
        res.append(osp.join(cfg.LOCAL_FOLDER_PATH, ch+'.txt'))
    return res

def select_hisd_slice(src_list, dst_list):
    for i in range(len(cfg.TARGET_CHANNEL)):
        for j in range(3):
            # print("SRC: ", src_list[i][j])
            # print("DST: ", dst_list[i][j])
            if src_list[i][j].endswith(".bz2"):
                with bz2.open(src_list[i][j], "rb") as srcf, open(dst_list[i][j], "wb") as dstf:
                    shutil.copyfileobj(srcf, dstf)
            else:
                shutil.copyfile(src_list[i][j], dst_list[i][j])