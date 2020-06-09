import os
import os.path as osp
import files
import config as cfg
import genImg


def get_target_data(sTT_file, target_lon_s, target_lat_s):
    """Get the target area.

    1. Calculate the grid according to the target longtitude and latitude,
       by the parameters from the file header.
    2. And get the target area by the slice of the STT data. 

    Args:
        sTT_file: File object
        target_lon_s: The start longtitude of the target area.
        target_lat_s: The start latitude of the target area.

    Returns:
        A 2-dim np array, contains the STT data.

    Raises:
        Exception: An error occurred when the input is out of range.
    """

    data_lon_s, data_lat_s = sTT_file.get_lonlat_start()
    data_lon_e, data_lat_e = sTT_file.get_lonlat_end()
    lon_per_grid, lat_per_grid = sTT_file.get_grid_per_lonlat()

    target_lon_grid_s = int((target_lon_s - data_lon_s) / lon_per_grid)
    target_lat_grid_s = int((target_lat_s - data_lat_s) / lat_per_grid)

    target_lon_e = target_lon_s + cfg.SPACE_RESOLUTION * cfg.SIZE
    target_lat_e = target_lat_s - cfg.SPACE_RESOLUTION * cfg.SIZE

    target_lon_grid_e = int((target_lon_e - data_lon_s) / lon_per_grid)
    target_lat_grid_e = int((target_lat_e - data_lat_s) / lat_per_grid)

    # Error handle
    if target_lon_s < data_lon_s or target_lat_s > data_lat_s or \
       target_lon_e > data_lon_e or target_lat_e < data_lat_e:
        raise Exception('Invalid longtitude or latitude!\n'
                        'Range:left top:({}, {}) right bottom:({}, {})'
                        .format(data_lon_s, data_lat_s, data_lon_e, data_lat_e))

    sTT_data = sTT_file.get_stt_data()
    area_data = sTT_data[target_lat_grid_s:target_lat_grid_e, target_lon_grid_s+1:target_lon_grid_e+1]
    return area_data



def main(lon_start, lat_start):
    file_list = os.listdir(cfg.INPUT_FOLDER_PATH)
    total = len(file_list)
    print('{} files total.'.format(len(file_list)))
    failed = 0
    for file_name in file_list:
        # TODO: error handle

        print('\rProcessing file {} ...'.format(file_name), end='')

        file_path = osp.join(cfg.INPUT_FOLDER_PATH, file_name)
        sTT_file = files.STTFile(file_path)
        # print(sTT_file)  # Show info.
        try:
            target_area_data  = get_target_data(sTT_file, lon_start, lat_start)
            genImg.gen_image(cfg.REAL_IMG_PATH, sTT_file, target_area_data)
        except Exception as e:
            print(e)
            failed += 1
    print('\nDone. {} successful, {} failed.'.format(total-failed, failed))

LON_START, LAT_START = 105, 45
main(LON_START, LAT_START)
