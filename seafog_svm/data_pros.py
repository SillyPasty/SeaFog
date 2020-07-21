import csv
import numpy as np
import os
import time


def get_dataset(file_path):
    x = []
    y = []

    for fn in os.listdir(file_path):
        file_name = os.path.join(file_path, fn)
        with open(file_name, 'r') as vfm_him_f:
            vfm_headers = ['lon', 'lat', 'real_time', 'him_time', 'fog_mask', 'land_water_mask']
            him_headers = ['B' + '{:0>2d}'.format(i) for i in range(1, 17)]
            headers = vfm_headers + him_headers

            reader = csv.DictReader(vfm_him_f, headers)

            for i, row in enumerate(reader):
                if i == 0:
                    continue
                y.append([int(row['fog_mask'])]) 
                x_tmp = []
                for c_headers in him_headers:
                    x_tmp += [int(row[c_headers])]
                x.append(x_tmp)

    x = np.array(x)
    y = np.array(y)
    return x, y

def get_filtered_dataset(file_path):
    dataset = {
        'sea_d':{'x':[], 'y':[]},
        'sea_n':{'x':[], 'y':[]},
        'land_d':{'x':[], 'y':[]},
        'land_n':{'x':[], 'y':[]}
    }

    for fn in os.listdir(file_path):
        file_name = os.path.join(file_path, fn)
        with open(file_name, 'r') as vfm_him_f:
            vfm_headers = ['lon', 'lat', 'real_time', 'him_time', 'fog_mask', 'land_water_mask']
            him_headers = ['B' + '{:0>2d}'.format(i) for i in range(1, 17)]
            headers = vfm_headers + him_headers

            reader = csv.DictReader(vfm_him_f, headers)

            for i, row in enumerate(reader):
                if i == 0:
                    continue

                x_tmp = []
                for c_headers in him_headers:
                    x_tmp += [int(row[c_headers])]
                
                tag = ''
                
                if row['land_water_mask'] == '1' and row['B04'] == '0':
                    # sea night
                    tag = 'sea_n'
                elif row['land_water_mask'] == '1' and row['B04'] != '0':
                    # sea day
                    tag = 'sea_d'
                elif row['land_water_mask'] == '0' and row['B04'] == '0':
                    # land night
                    tag = 'land_n'
                elif row['land_water_mask'] == '0' and row['B04'] != '0':
                    # land day
                    tag = 'land_d'

                dataset[tag]['y'].append([int(row['fog_mask'])])
                dataset[tag]['x'].append(x_tmp)

    for k in dataset:
        dataset[k]['x'] = np.array(dataset[k]['x'])
        dataset[k]['y'] = np.array(dataset[k]['y'])
    return dataset

def sampling(x, y):
    z = np.hstack((x,y))
    np.random.seed(0)
    np.random.shuffle(z)
    pos_total = np.sum(y)
    neg_count = 0
    new_x = []
    new_y = []
    for zz in z:
        if neg_count < pos_total or zz[-1] == 1:
            new_x.append(zz[:16])
            new_y.append([zz[-1]])
            if zz[-1] == 0:
                neg_count += 1

    return np.array(new_x), np.array(new_y)