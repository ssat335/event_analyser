import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
import random

from HapsNonHapsDetector import HapsNonHapsDetector
from ClusterEvents import ClusterEvents



filt_data = sio.loadmat('../CM_filt_raw_data.mat')
data_in = filt_data['filtData']#[:, 124796:133751]

detector = HapsNonHapsDetector(data_in)
detector.showHapsNonHaps()
data_label = detector.obtainHapsNonHapsLabel()

cluster_mat = ClusterEvents(data_label).getClusteredEventsAsMatrix()


def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

plt.figure()
cmap = get_cmap(100)
map_colour = {}
for val in np.nditer(np.unique(cluster_mat)):
    map_colour[int(val)] = cmap(random.randint(0, 100))

horizontal_spacing = 100
for channel in range(0,data_in.shape[0]):
    plt.plot(data_in[channel, :] + horizontal_spacing * channel, c='gray' )
    for c in np.nditer(np.unique(cluster_mat)):
        if int(c) is 0:
            pass
        else:
            indexes = np.where(cluster_mat[channel, :] == int(c))
            cmap_val = np.random.rand(3,)
            plt.plot(indexes, data_in[channel, indexes] + horizontal_spacing * channel, 'o', mfc=None, markersize=5, c=map_colour[int(c)])
plt.show()
