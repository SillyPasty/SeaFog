

def count_l_w_mask(hdf_file):
    lw_mask = hdf_file.select('Land_Water_Mask').get()
    land_mask = [1, 2]
    water_mask = [0, 3, 4, 5, 6, 7]
    land_cnt = 0
    water_cnt = 0
    for ss in lw_mask:
        mask = ss[0]
        
        if land_mask.count(mask) > 0: land_cnt += 1
        elif water_mask.count(mask) > 0: water_cnt += 1
    return land_cnt, water_cnt

def count_single_shot(hdf_file):
    datas = hdf_file.select('Feature_Classification_Flags').get()
    return datas.shape[0]