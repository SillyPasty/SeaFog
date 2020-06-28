import numpy as np
import config as cfg

class TBBFile():
    def __init__(self, file_name):
        with open(file_name) as f:
            self.channel = file_name[-7:-4]
            self.tbb_data = np.zeros((cfg.SIZE_HEIGHT, cfg.SIZE_WIDTH))
            for row, line in enumerate(f.readlines()):
                tbb_row = np.array([float(x) for x in line.strip().split(' ')])
                self.tbb_data[row] = tbb_row
            
            self.tbb_data_mask = self.tbb_data != -1
            self.tbb_data = np.multiply(self.tbb_data, self.tbb_data_mask)


    def get_shape(self):
        return self.tbb_data.shape
