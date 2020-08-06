import csv
import numpy as np
import os
import time
from datetime import datetime
from pysolar import solar
from pytz import timezone


class Dataset():

    def __init__(self, data_path, range_dic, prefix):
        # B01~B03 visible
        # B04~B06 near infrared
        # B06~B16 infrared
        self.data_path = data_path
        self.prefix = prefix
        self.csv_path, self.np_path = self.__init_data_path()
        self.lat1, self.lat2 = range_dic['lat1'], range_dic['lat2']
        self.lon1, self.lon2 = range_dic['lon1'], range_dic['lon2']
        self.tags = ['_sea_d', '_sea_n', '_land_d', '_land_n']
        self.ds_namelist = self.__get_ds_name_list()
        if not all([os.path.exists(name + '.npz') for name in self.ds_namelist]):
            print('New data, generating npz files...')
            self.dataset = self.__gen_dataset()
            self.__save_dataset()
        self.dataset = self.__read_dataset()

    def get_dataset(self, sldn_dic):
        X = None
        Y = None
        if sldn_dic['sea'] and sldn_dic['day']:
            tmp_x, tmp_y = self.dataset['_sea_d']['x'], self.dataset['_sea_d']['y']
            X = tmp_x if X is None else np.concatenate((X, tmp_x), axis=0)
            Y = tmp_y if Y is None else np.concatenate((Y, tmp_y), axis=0)
        if sldn_dic['sea'] and sldn_dic['night']:
            tmp_x, tmp_y = self.dataset['_sea_n']['x'], self.dataset['_sea_n']['y']
            X = tmp_x if X is None else np.concatenate((X, tmp_x), axis=0)
            Y = tmp_y if Y is None else np.concatenate((Y, tmp_y), axis=0)
        if sldn_dic['land'] and sldn_dic['day']:
            tmp_x, tmp_y = self.dataset['_land_d']['x'], self.dataset['_land_d']['y']
            X = tmp_x if X is None else np.concatenate((X, tmp_x), axis=0)
            Y = tmp_y if Y is None else np.concatenate((Y, tmp_y), axis=0)
        if sldn_dic['land'] and sldn_dic['night']:
            tmp_x, tmp_y = self.dataset['_land_n']['x'], self.dataset['_land_n']['y']
            X = tmp_x if X is None else np.concatenate((X, tmp_x), axis=0)
            Y = tmp_y if Y is None else np.concatenate((Y, tmp_y), axis=0)
        return X, Y
    
    def pn_sampling(self, X, Y, ratio = 1):
        z = np.hstack((X, Y))
        np.random.seed(0)
        np.random.shuffle(z)
        pos_total = np.sum(Y)
        neg_total = pos_total * ratio
        neg_count = 0
        new_x, new_y = [], []
        for zz in z:
            if neg_count < neg_total or zz[-1] == 1:
                new_x.append(zz[:-1])
                new_y.append([zz[-1]])
                if zz[-1] == 0:
                    neg_count += 1
        X, Y = np.array(new_x), np.array(new_y)
        return X, Y

    def analysis(self, X, Y):
        sample_total = Y.shape[0]
        pos_total = np.sum(Y)
        neg_total = sample_total - pos_total
        print('Total samples: {}\n Positive samples: {}, Negative samples: {}'.format(sample_total, pos_total, neg_total))

    
    def __get_ds_name_list(self):
        latlon_range = '_{}_{}_{}_{}'.format(self.lat1, self.lon1, self.lat2, self.lon2)
        ds_n_list = []
        for tag in self.tags:
            dataset_path = os.path.join(self.np_path, self.prefix + 'np' + tag + latlon_range)
            ds_n_list.append(dataset_path)
        return ds_n_list

    def __init_data_path(self):
        csv_path = os.path.join(self.data_path, 'csv_ds')
        np_path = os.path.join(self.data_path, 'np_ds')
        if not os.path.exists(np_path):
            os.mkdir(np_path)
        if not os.path.exists(csv_path):
            print('No csv dir!')
        return csv_path, np_path

    def __gen_dataset(self):
        dataset = {
            '_sea_d':{'x':[], 'y':[]},
            '_sea_n':{'x':[], 'y':[]},
            '_land_d':{'x':[], 'y':[]},
            '_land_n':{'x':[], 'y':[]}
        }

        def add_solar_angle(row):
            him_headers = ['B' + '{:0>2d}'.format(i) for i in range(1, 17)]
            x_tmp = []

            for c_headers in him_headers:
                x_tmp += [int(row[c_headers])]

            dt = datetime.strptime(row['him_time'], '%Y-%m-%d %H:%M:%S').replace(tzinfo = timezone('UTC'))
            solar_angle = solar.get_altitude(float(row['lat']), float(row['lon']), dt)
            x_tmp += [solar_angle]
            x_tmp += [dt.timestamp()]
            x_tmp += [int(row['land_water_mask'])]
            return x_tmp

        for fn in os.listdir(self.csv_path):
            file_name = os.path.join(self.csv_path, fn)
            with open(file_name, 'r') as vfm_him_f:
                vfm_headers = ['lon', 'lat', 'real_time', 'him_time', 'fog_mask', 'land_water_mask']
                him_headers = ['B' + '{:0>2d}'.format(i) for i in range(1, 17)]
                headers = vfm_headers + him_headers

                reader = csv.DictReader(vfm_him_f, headers)

                for i, row in enumerate(reader):
                    if i == 0:
                        continue
                    lat, lon = float(row['lat']), float(row['lon'])
                    if lat > self.lat1 or lat < self.lat2 or lon > self.lon2 or lon < self.lon1:
                        continue
                    x_single = add_solar_angle(row)

                    tag = ''

                    if row['land_water_mask'] == '1' and row['B04'] == '0':
                        # sea night
                        tag = '_sea_n'
                    elif row['land_water_mask'] == '1' and row['B04'] != '0':
                        # sea day
                        tag = '_sea_d'
                    elif row['land_water_mask'] == '0' and row['B04'] == '0':
                        # land night
                        tag = '_land_n'
                    elif row['land_water_mask'] == '0' and row['B04'] != '0':
                        # land day
                        tag = '_land_d'

                    dataset[tag]['y'].append([int(row['fog_mask'])])
                    dataset[tag]['x'].append(x_single)

        for k in dataset:
            dataset[k]['x'] = np.array(dataset[k]['x'])
            dataset[k]['y'] = np.array(dataset[k]['y'])
        return dataset

    def __save_dataset(self):
        for tag, fn in zip(self.tags, self.ds_namelist):
            np.savez(fn, x=self.dataset[tag]['x'], y=self.dataset[tag]['y'])

    def __read_dataset(self):
        dataset = {}
        for tag, fn in zip(self.tags, self.ds_namelist):
            dataset[tag] = np.load(fn + '.npz')
        return dataset
