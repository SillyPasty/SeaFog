from datetime import datetime
import os
from openpyxl import load_workbook

def save_error(file_path, tag):
    analysis_path = file_path + '.xlsx'
    wb = load_workbook(analysis_path)
    wb.create_sheet(tag)
    sheet = wb.get_sheet_by_name(tag)
    clodk_cnt = [[1, 2, 3], ['asd', 'asd', 'test']]
    for i in clock_cnt:
        sheet.append(i)
    wb.save(analysis_path)

def get_error_anal(file_path, tag):
    save_error(file_path, tag)

get_error_anal('test', '233')