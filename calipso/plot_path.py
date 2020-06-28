import numpy as np
import cv2

SPACE_R = 0.0125
START_LON = 105
START_LAT = 45
SIZE_WIDTH = 3602
SIZE_HEIGHT = 2162

def get_single_path(hdf_file, img):
    ss_lat = hdf_file.select('ssLatitude')
    ss_lat_data = ss_lat.get()
    ss_lon = hdf_file.select('ssLongitude')
    ss_lon_data = ss_lon.get()
    # print(ss_lat_data[0], ss_lon_data[0])
    # print(ss_lat_data[-1], ss_lon_data[-1])
    # print('---')


    def gen_lonlat_img():
        for lat, lon in zip(ss_lat_data, ss_lon_data):
            lat_cell = (int)((lat - START_LAT) / -SPACE_R)
            lon_cell = (int)((lon - START_LON) / SPACE_R)
            img[lat_cell, lon_cell] = 255
    gen_lonlat_img()
    
    return img

def get_spacecraft_position(hdf_file):
    space_position = hdf_file.select('Spacecraft_Position').get()
    print(space_position.shape)
    print(space_position)
