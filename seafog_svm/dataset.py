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
        if not (all([os.path.exists(name + '.npz') for name in self.ds_namelist]) \
            and os.path.exists(self.info_dic_name + '.npy')):
            print('New data, generating files...')
            self.dataset, self.info_dic = self.__gen_dataset()
            self.__save_dataset()
        else:
            print('Data exists, reading files...')
            self.dataset, self.info_dic = self.__read_dataset()

    def get_dataset(self, sldn_dic):
        X = None
        Y = None
        tags = []
        if sldn_dic['sea'] and sldn_dic['day']:
            tags.append('_sea_d')
        if sldn_dic['sea'] and sldn_dic['night']:
            tags.append('_sea_n')
        if sldn_dic['land'] and sldn_dic['day']:
            tags.append('_land_d')
        if sldn_dic['land'] and sldn_dic['night']:
            tags.append('_land_n')

        for tag in tags:
            tmp_x, tmp_y = self.dataset[tag]['x'], self.dataset[tag]['y']
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

    def get_info_dic(self):
        return self.info_dic

    def __get_ds_name_list(self):
        latlon_range = '_{}_{}_{}_{}'.format(self.lat1, self.lon1, self.lat2, self.lon2)
        self.info_dic_name = os.path.join(self.np_path, self.prefix + 'info_dic' + latlon_range)
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
        info_dic = {}

        def add_solar_angle(row):
            him_headers = ['B' + '{:0>2d}'.format(i) for i in range(1, 17)]
            x_tmp = []

            for c_headers in him_headers:
                x_tmp += [int(row[c_headers])]

            dt = datetime.strptime(row['him_time'], '%Y-%m-%d %H:%M:%S').replace(tzinfo = timezone('UTC'))
            solar_angle = solar.get_altitude(float(row['lat']), float(row['lon']), dt)
            x_tmp += [solar_angle]
            return x_tmp

        sample_count = 0
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
                    if int(row['B01']) == -1:
                        continue
                    # save the info into dic
                    info_headers = headers
                    sample_info = [row[tag] for tag in info_headers]
                    info_dic[sample_count] = sample_info
                    # add solar angle
                    x_single = add_solar_angle(row)
                    x_single += [sample_count]
                    sample_count += 1

                    # Get day & night tag
                    tag = ''
                    channel_tags = ['B' + '{:0>2d}'.format(i) for i in range(1, 6)]
                    dt = datetime.strptime(row['him_time'], '%Y-%m-%d %H:%M:%S').replace(tzinfo = timezone('UTC'))
                    night_flag = (dt.hour >= 16)
                    sea_flag = row['land_water_mask'] == '1'

                    if sea_flag and night_flag:
                        # sea night
                        tag = '_sea_n'
                    elif sea_flag and not night_flag:
                        # sea day
                        tag = '_sea_d'
                    elif not sea_flag and night_flag:
                        # land night
                        tag = '_land_n'
                    elif not sea_flag == '0' and not night_flag:
                        # land day
                        tag = '_land_d'

                    dataset[tag]['y'].append([int(row['fog_mask'])])
                    dataset[tag]['x'].append(x_single)

        for k in dataset:
            dataset[k]['x'] = np.array(dataset[k]['x'])
            dataset[k]['y'] = np.array(dataset[k]['y'])

        return dataset, info_dic

    def __save_dataset(self):
        np.save(self.info_dic_name, self.info_dic)
        for tag, fn in zip(self.tags, self.ds_namelist):
            np.savez(fn, x=self.dataset[tag]['x'], y=self.dataset[tag]['y'])

    def __read_dataset(self):
        dataset = {}
        info_dic = np.load(self.info_dic_name + '.npy', allow_pickle=True).item()
        for tag, fn in zip(self.tags, self.ds_namelist):
            dataset[tag] = np.load(fn + '.npz')
        return dataset, info_dic
