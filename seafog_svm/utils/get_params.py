import csv

def get_params(parameter_path):
    range_headers = ['lat1', 'lon1' ,'lat2' ,'lon2']
    sldn_headers = ['day' ,'night' ,'sea' ,'land']
    headers = range_headers + sldn_headers
    range_dic_list, sldn_dic_list = [], []

    with open(parameter_path, 'r') as f:

        reader = csv.DictReader(f, headers)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            range_dic, sldn_dic = {}, {}
            for range_tag in range_headers:
                range_dic[range_tag] = float(row[range_tag])

            for sldn_tag in sldn_headers:
                sldn_dic[sldn_tag] = True if int(row[sldn_tag]) == 1 else False

            range_dic_list.append(range_dic)
            sldn_dic_list.append(sldn_dic)
    return range_dic_list, sldn_dic_list