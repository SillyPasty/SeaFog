from pyhdf.SD import SD
import numpy as np
import cv2
import os
import os.path as osp
from vfm import VFM
from cfg import GenCfg
from datetime import datetime, timedelta

class CalipsoFile():
    
    def __init__(self, file_dir, file_name):
        self.hdf_file = SD(osp.join(file_dir, file_name))
        self.vfm = VFM(self.hdf_file, file_name)
        self.file_name = file_name

    def get_general_info(self):
        datasets_dic = self.hdf_file.datasets()
        for idx,sds in enumerate(datasets_dic.keys()):
            print(idx, sds)

    def plot_path_with_mask(self, img, fog_mask_ratio):
        ss_lat_data = self.hdf_file.select('ssLatitude').get()
        ss_lon_data = self.hdf_file.select('ssLongitude').get()
        fog_mask = self.get_vfm_fog_mask(fog_mask_ratio)
        for lat, lon, fog in zip(ss_lat_data, ss_lon_data, fog_mask):
            lat_cell = (int)((lat - GenCfg.START_LAT) / -GenCfg.SPACE_R)
            lon_cell = (int)((lon - GenCfg.START_LON) / GenCfg.SPACE_R)
            img[lat_cell, lon_cell, 0] = 255
            img[lat_cell, lon_cell, 1] = 0
            img[lat_cell, lon_cell, 2] = 0
            if fog == 1:
                img[lat_cell, lon_cell, 0] = 0
                img[lat_cell, lon_cell, 2] = 255
        return img

    def get_plot_path(self, img):
        ss_lat_data = self.hdf_file.select('ssLatitude').get()
        ss_lon_data = self.hdf_file.select('ssLongitude').get()
        for lat, lon in zip(ss_lat_data, ss_lon_data):
            lat_cell = (int)((lat - GenCfg.START_LAT) / -GenCfg.SPACE_R)
            lon_cell = (int)((lon - GenCfg.START_LON) / GenCfg.SPACE_R)
            if lat_cell >= img.shape[0]:
                lat_cell = img.shape[0] - 1
            if lon_cell >= img.shape[1]:
                lon_cell = img.shape[1] - 1
            img[lat_cell, lon_cell, 0] = 0
        return img

    def get_lon_lat(self):
        ss_lat = self.hdf_file.select('ssLatitude').get()
        ss_lon = self.hdf_file.select('ssLongitude').get()
        return ss_lon, ss_lat

    def count_valid_ss(self, threshold, clock_count):
        result_dic = {'total': 0, 'land': 0, 'water': 0}

        if self.is_valid_file(threshold):
            hour, minute = self.get_seperate_clocks()
            shift = 0
            if minute < 15: shift = 0
            elif minute > 45: shift = 2
            else: shift = 1
            hour = (hour + 8) % 24
            clock_count[(2 * hour + shift) % 48] += 1

            lw_mask = self.hdf_file.select('ssLand_Water_Mask').get()
            land_mask = [1, 2]
            water_mask = [0, 3, 4, 5, 6, 7]
            for ss in lw_mask:
                mask = ss[0]
                if land_mask.count(mask) > 0: result_dic['land'] += 1
                elif water_mask.count(mask) > 0: result_dic['water'] += 1
            
            result_dic['total'] = self.vfm.get_shape()[1]

        return clock_count, result_dic

    def is_valid_file(self, threshold):
        time_data = self.get_time()
        start_dt = self.parse_ss_time(time_data[0, 0])
        end_dt = self.parse_ss_time(time_data[-1, 0])
        s_min, e_min = start_dt.minute, end_dt.minute
        if (e_min <= threshold and (60 - threshold <= s_min or s_min <= threshold)) or \
           (e_min <= 30 + threshold and (30 - threshold <= s_min or s_min <= 30 + threshold)):
            return True
        return False

    def get_seperate_clocks(self):
        time_data = self.get_time()
        dt = self.parse_ss_time(time_data[0, 0])
        hour = dt.hour
        minute = dt.minute
        return hour, minute
    
    def get_start_time(self):
        time_data = self.get_time()
        start_dt = self.parse_ss_time(time_data[0, 0])
        return start_dt

    def get_time(self):
        datas = self.hdf_file.select('ssProfile_UTC_Time').get()
        return datas

    def parse_ss_time(self, ss_time):
        time_str = str(ss_time)
        form = '%y%m%d'
        time = datetime.strptime(time_str[:6], form)
        fraction = float(time_str[6:])
        delta = timedelta(seconds = 24 * 3600 * fraction)
        time += delta
        return time

    def get_land_water_mask(self):
        # 
        # ocean_mask = [0, 6, 7]
        lw = self.hdf_file.select('ssLand_Water_Mask').get()
        ma = np.bitwise_or(lw >= 6, lw == 0)

        land_water_mask = np.zeros((lw.shape), dtype=np.int)
        land_water_mask += ma * 1

        return land_water_mask

    def get_vfm_fog_mask(self, ratio, height = 500):
        return self.vfm.get_fog_mask(ratio, height)
    
    def plot_vfm(self, result_path, show=False):
        self.vfm.plot(result_path, show)
    
    def get_plot_vfm(self):
        return self.vfm.get_plot_vfm()