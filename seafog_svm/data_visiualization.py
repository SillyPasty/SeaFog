import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import time

from dataset import Dataset
import config as cfg

range_dic = {'lat1': 41., 'lon1': 117.5, 'lat2': 34., 'lon2': 127.}
sldn_dic = {'sea': True, 'land': False,'day': True, 'night': False}

def plot(X, Y):
    plt.title('Analysis')
    for x, y in zip(X, Y):
        plt.scatter(x[0], x[1], c='red' if y == 0 else 'blue')
    plt.show()
    return None

def t_sne(data_path, range_dic):
    dataset = Dataset(data_path, range_dic, cfg.DATA_PREFIX)
    X, Y = dataset.get_dataset(sldn_dic)
    X, Y = dataset.pn_sampling(X, Y)
    dataset.analysis(X, Y)
    X = X[:,:-1]
    tsne = TSNE(perplexity=50, verbose=True, n_iter=10000, learning_rate=200)
    X_embedded = tsne.fit_transform(X)
    return X_embedded, Y

def main():
    start_time = time.time()
    X, Y = t_sne(cfg.DATA_PATH, range_dic)
    plot(X, Y)
    print('Total time:' + str(time.time() - start_time))

main()