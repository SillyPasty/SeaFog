import os
import os.path as osp
from matplotlib import pyplot as plt
from calipso_file import CalipsoFile


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
            print('\r' + fn, end='')
            total_cnt += 1
            calipso_file = CalipsoFile(FILE_FOLDER, fn)
            clock_cnt, count_dir = calipso_file.count_valid_ss(threshold, clock_cnt)
            if count_dir['total'] != 0:
                cnt += 1
                total_data_cnt += count_dir['total']
                land_data_cnt += count_dir['land']
                water_data_cnt += count_dir['water']

    return clock_cnt, cnt, total_cnt, land_data_cnt, water_data_cnt, total_data_cnt


clock_cnt = [0 for x in range(48)]
clock_cnt, cnt, total_cnt, land_data_cnt, water_data_cnt, total_data_cnt = count_valid_file(3, clock_cnt)
print(str(total_cnt) + 'total,' + str(cnt) + 'valid')
print(str(total_data_cnt) + ' points; ' + 'land:' + str(land_data_cnt) + ' water:' + str(water_data_cnt))
plot_valid_time(clock_cnt)