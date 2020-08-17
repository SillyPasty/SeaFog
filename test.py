import math
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

# fun1()
print(math.log10(0.0223))