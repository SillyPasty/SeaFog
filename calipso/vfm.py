import numpy as np
from vfm_util.get_vfm import get_vfm
import math
import cv2
import os.path as osp
from cfg import VfmCfg

class VFM():
    def __init__(self, hdf_file, fn):
        self.vfm = get_vfm(hdf_file)
        self.file_name = fn

    def plot(self, result_file_dir, show):
        img = self.get_plot_vfm()
        img_name = osp.join(result_file_dir, self.file_name[:-3])
        if show:
            cv2.imshow('result', img)
            cv2.waitKey(0)
        else:
            cv2.imwrite(img_name + 'png', img)
            print('File write to ' + img_name + 'png')
        
    def get_plot_vfm(self):
        """
        Extracts feature type for each element in a vertical feature mask array:

            0 = invalid (bad or missing data)  black
            1 = 'clear air'                    red
            2 = cloud                          light blue
            3 = aerosol                        yellow
            4 = stratospheric feature          pink
            5 = surface                        dark blue
            6 = subsurface                     green
            7 = no signal (totally attenuated)
        """
        img = np.zeros((self.vfm.shape[0], self.vfm.shape[1], 3), dtype=np.uint8)
        colors = [[0, 0, 0], [0, 0, 255], [220, 220, 0], [0, 220, 220], [220, 0, 220], [255, 0, 0], [0, 255, 0], [0, 0, 0]]
        for i, rows in enumerate(self.vfm):
            for j, cell in enumerate(rows):
                img[i, j] = colors[cell]

        return img

    def get_fog_mask(self ,ratio, height):
        """
            Vertical feature mask array:

                0 = invalid (bad or missing data)  black
                1 = 'clear air'                    red
                2 = cloud                          light blue
                3 = aerosol                        yellow
                4 = stratospheric feature          pink
                5 = surface                        dark blue
                6 = subsurface                     green
                7 = no signal (totally attenuated)
        """
        y_axis, x_axis = self.vfm.shape
        seafog_mask = np.zeros((x_axis, 1), dtype=np.int)
        valid_mask = [2]
        invalid_mask = [0, 5, 6, 7]

        for x in range(x_axis):
            fog_threshold = math.ceil((height - VfmCfg.START_ALT) / VfmCfg.RESOLUTION)
            fog_count, total_count = 0, 0
            y = y_axis - 1
            while True:
                if y < VfmCfg.MAXIMUM_CELL:
                    y = -1
                    break
                cell_data = self.vfm[y, x]
                if invalid_mask.count(cell_data) == 0:
                    break
                y -= 1
        
            fog_threshold = y - fog_threshold

            while y >= 0 and y > fog_threshold:
                cell_data = self.vfm[y, x]
                y -= 1
                total_count += 1
                if valid_mask.count(cell_data) != 0:
                    fog_count += 1
            if total_count != 0 and (fog_count / total_count) >= ratio:
                seafog_mask[x] = 1
            # if total_count == 0:
            #     seafog_mask[x] = 0
        
        return seafog_mask

    def get_shape(self):
        return self.vfm.shape

