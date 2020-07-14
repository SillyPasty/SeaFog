import os
import csv

FILE_FOLDER = r'calipso\result_data\him_dataset'
def count(file_name, stat):
    with open(file_name, 'r') as vfm_him_f:
        vfm_headers = ['lon', 'lat', 'real_time', 'him_time', 'fog_mask', 'land_water_mask']
        him_headers = ['B' + '{:0>2d}'.format(i) for i in range(1, 17)]
        headers = vfm_headers + him_headers

        reader = csv.DictReader(vfm_him_f, headers)

        for i, row in enumerate(reader):
            if i == 0:
                continue
            fog_mask = int(row['fog_mask'])
            lw_mask = int(row['land_water_mask'])

            stat['total'] += 1
            stat['total_fog'] += fog_mask
            stat['total_ocean'] += lw_mask
            stat['ocean_fog'] += fog_mask & lw_mask
            stat['land_fog'] += fog_mask & ~lw_mask



def main(file_folder):
    stat = {'total': 0, 'total_fog': 0, 'total_ocean': 0,
            'land_fog': 0, 'ocean_fog': 0}
    
    for fn in os.listdir(file_folder):
        fn = os.path.join(file_folder, fn)
        count(fn, stat)

    stat['fog_percent'] = stat['total_fog'] / stat['total']
    stat['sea_fog_percent'] = stat['ocean_fog'] / stat['total']
    stat['land_fog_percent'] = stat['land_fog'] / stat['total']
    stat['sea_fog_sea_percent'] = stat['ocean_fog'] / stat['total_ocean']

    print('Total points: {total}\n'.format(**stat) +
          'Total fog points: {total_fog}, Fog / Total: {fog_percent}\n'.format(**stat) +
          'Total ocean fog points: {ocean_fog}, Ocean_fog / Ocean: {sea_fog_sea_percent}'.format(**stat))

main(FILE_FOLDER)
