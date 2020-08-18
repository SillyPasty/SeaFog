import math
import datetime
import numpy as np
def fun1():
    while True:
        x = float(input('X:'))
        log_root = math.log10(0.0223)
        denom = (1 - log_root) * 0.75
        y = (10**(x*denom/255 + log_root)) * 255
        print(y)

def fun2():
    while True:
        x = float(input('X:'))
        log_root = math.log10(0.0223)
        denom = (1 - log_root) * 0.75
        y = (math.log10(x/255) - log_root) * 255 / denom
        print(y)

def fun3():
    lis = []
    arr1 = np.asarray([[1, 2, 3, 5], [1, 3, 4, 5], [1, 1, 1, 1]])
    print(arr1)
    arr2 = np.asarray([[6, 6, 6, 1], [7, 8, 3, 1], [1, 2, 3, 4]])
    lis.append(arr1)
    lis.append(arr2)
    arr8 = np.asarray([[[6], [6], [6], [1]], [[7], [8], [3], [1]], [[1], [2], [3], [4]]])
    arr3 = np.asarray(lis)
    print(arr3.shape)
    arr3 = arr3.transpose(1, 2, 0)
    print(arr3.shape)
    print(arr8.shape)
    arr3 = np.concatenate((arr3, arr8), axis=2)
    print(arr3.shape)
    return
    arr3 = np.asarray(lis)
    arr4 = arr3.reshape(-1, 2)
    
    print(arr4.shape)
    print(arr4)
    arr5 = arr4.reshape(3, 4, 2)
    shape = arr5.shape
    print(type(shape))
    print(arr5.shape)

# fun1()
# print(math.log10(0.0223))
# assert 1!=1, print(1)
# fun3()
dt = datetime.datetime(year=2020, month=2, day=31)
print(dt)