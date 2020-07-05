import os
import os.path as osp
from matplotlib import pyplot as plt
from pyhdf.SD import SD
from file_data_cnt import count_l_w_mask, count_single_shot


EXAMPLE_FILENAME = r"CAL_LID_L2_VFM-Standard-V4-20.2018-05-14T04-46-55ZD_Subset.hdf"
FILE_FOLDER = r"calipso\data\2019"
time_stamp = []
def plot_valid_time(clock_cnt):

    x_axis_labels = ['0:00', '0:30', '1:00', '1:30', '2:00', '2:30', '3:00', '3:30', 
                        '4:00', '4:30', '5:00', '5:30', '6:00', '6:30', '7:00', '7:30',
                        '8:00', '8:30', '9:00', '9:30', '10:00', '10:30', '11:00', '11:30',
                        '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30',
                        '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
                        '20:00', '20:30', '21:00', '21:30', '22:00', '22:30', '23:00', '23:30']
    plt.title('Analysis')
    plt.bar(x_axis_labels, clock_cnt)
    plt.xticks(rotation=270)
    plt.show()
    
    

def count_valid_file(threshold, clock_cnt):
    cnt = 0
    total_cnt = 0
    total_data_cnt = 0
    land_data_cnt = 0
    water_data_cnt = 0
    for fn in os.listdir(FILE_FOLDER):
        if fn[-4:] == '.hdf':
            total_cnt += 1
            min_dif = get_min_dif_minute(fn)
            if min_dif < threshold:
                hour, minute = get_seperate_clocks(fn)
                shift = 0
                if minute < 15: shift = 0
                elif minute > 45: shift = 2
                else: shift = 1
                hour = (hour + 8) % 24
                clock_cnt[(2 * hour + shift) % 48] += 1
                cnt += 1

                hdf_file = SD(osp.join(FILE_FOLDER, fn))
                total_data_cnt += count_single_shot(hdf_file)
                l_d_c, w_d_c = count_l_w_mask(hdf_file)
                land_data_cnt += l_d_c
                water_data_cnt += w_d_c

    return clock_cnt, cnt, total_cnt, land_data_cnt, water_data_cnt, total_data_cnt

def get_seperate_clocks(filename):
    datetime_str = filename[30:49]
    time_str = datetime_str[11:20]
    hour_str = time_str[0:2]
    min_str = time_str[3:5]
    hour = int(hour_str)
    minute = int(min_str)
    return hour, minute
    
def get_min_dif_minute(filename):
    _, minute = get_seperate_clocks(filename)
    dif1 = abs(minute - 0)
    dif2 = abs(minute - 30)
    dif3 = abs(minute - 60)
    min_dif = min(dif1, dif2, dif3)
    return min_dif

clock_cnt = [0 for x in range(48)]
clock_cnt, cnt, total_cnt, land_data_cnt, water_data_cnt, total_data_cnt = count_valid_file(3, clock_cnt)
print(str(total_cnt) + 'total,' + str(cnt) + 'valid')
print(str(total_data_cnt) + ' points; ' + 'land:' + str(land_data_cnt) + ' water:' + str(water_data_cnt))
plot_valid_time(clock_cnt)