from datetime import datetime
import os
from openpyxl import load_workbook

from pytz import timezone

dt = datetime.strptime('2018-1-24  17:00:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo = timezone('UTC'))
print(dt)
timestamp = dt.timestamp()
dt = datetime.fromtimestamp(timestamp, tz=timezone('UTC'))
print(dt)
x = []
x += [1]
x += ['1']
def foo():
    x1 = {'x': 5}
    x2 = {}
    x2[1] = [12, 3]
    return x1, x2
x1, x2 = foo()
print(x1, x2)