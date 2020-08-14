import platform
import os
MAIN_PATH = 'seafog_svm' if (platform.system() == "Windows") else ''
SVC_MODEL_PATH = os.path.join(MAIN_PATH, 'model', 'svc')
XGB_MODEL_PATH = os.path.join(MAIN_PATH, 'model', 'xgb')
DATA_PATH = os.path.join(MAIN_PATH, 'data')
OUTPUT_PATH = os.path.join(MAIN_PATH, 'output')
DATA_PREFIX = '18'