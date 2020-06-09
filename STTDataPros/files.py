import numpy as np
import config as cfg

class STTFile():
    """ The STT file class, contains the header and data.

    Attributes:
        MASK: A class variable, used to store and represent which grid is valid.
        __header: Header.

    """
    MASK = None
    def __init__(self, file_path):
        with open(file_path, encoding='utf-8') as f:
            info_list = []
            self.__header = {}
            for i in range(3):
                line = f.readline()
                if i == 0:
                    self.__header['Description'] = line.strip()
                elif i == 1 or i == 2:
                    info_list += line.strip().split('\t')

            self.__header['date']= '20{}-{}-{}'.format(info_list[0], info_list[1], info_list[2])
            self.__header['time'] = '{}-{}'.format(info_list[3], info_list[4])
            self.__header['slice'] = info_list[5]
            self.__header['lon_per_grid'], self.__header['lat_per_grid'] = float(info_list[6]), float(info_list[7])            
            self.__header['lon_start'], self.__header['lon_end'] = float(info_list[8]), float(info_list[9])
            self.__header['lat_start'], self.__header['lat_end'] = float(info_list[10]), float(info_list[11])
            self.__header['lon_pix'], self.__header['lat_pix'] = int(info_list[12]), int(info_list[13])
            self.__header['eva'], self.__header['eva_start'], self.__header['eva_end'] = \
                float(info_list[14]), float(info_list[15]), float(info_list[16])
            self.__header['smooth_param'] = float(info_list[17])
            self.__header['bold_param'] = float(info_list[18])

            self.__sTT = np.zeros((self.__header['lat_pix'], self.__header['lon_pix']))
            block_row = []
            rows = 0
            for line in f.readlines():
                stt_row = np.array([float(x) for x in line.strip().split('\t')])
                block_row = np.concatenate((block_row, stt_row))
                if len(stt_row) == 1:
                    self.__sTT[rows] = block_row
                    rows += 1
                    block_row = []
            
            if f.name.endswith('.000'):
                STTFile.MASK = self.__sTT == cfg.K_MAX

            self.__sTT = np.multiply(self.__sTT, ~STTFile.MASK)
            self.__sTT = np.ma.array(self.__sTT, mask = STTFile.MASK)

    def get_stt_data(self):
        return self.__sTT
    
    def get_lonlat_start(self):
        return self.__header['lon_start'], self.__header['lat_start']
    
    def get_lonlat_end(self):
        return self.__header['lon_end'], self.__header['lat_end']
    
    def get_grid_per_lonlat(self):
        return self.__header['lon_per_grid'], self.__header['lat_per_grid']
    
    def get_datetime(self):
        return self.__header['date'], self.__header['time']

    def __str__(self):
        result  = "Headline: {}\n".format(self.__header['Description'])
        result += "Time: {} {}\n".format(self.__header['date'], self.__header['time'])
        result += "Pix lon distance: {:<5} Pix lat distance: {:<5}\n".format(self.__header['lon_per_grid'], self.__header['lat_per_grid'])
        result += "Start longitude:  {:<5} Start latitude:   {:<5}\n".format(self.__header['lon_start'], self.__header['lat_start'])
        result += "End longitude:    {:<5} End latitude:     {:<5}\n".format(self.__header['lon_end'], self.__header['lat_end'])
        result += "Pix number lon:   {:<5} Pix number lat:   {:<5}\n".format(self.__header['lon_pix'], self.__header['lat_pix'])
        result += "Eva line:         {:<5} Eva start:        {:<5}  Eva end: {:<5}\n". \
            format(self.__header['eva'], self.__header['eva_start'], self.__header['eva_end'] )
        result += "Smooth factor:    {:<5} Bold factor       {:<5}".format(self.__header['smooth_param'], self.__header['bold_param'])
        
        return result
