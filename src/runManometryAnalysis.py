"""Detect HAPS and Non-HAPS events in manometry experiments and plot them as clustered events."""

import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
import random


__author__ = "Shameer Sathar, https://github.com/ssat335"
__version__ = "0.0.1"

from HapsNonHapsDetector import HapsNonHapsDetector
from ClusterEvents import ClusterEvents

# load the dataset as rows (channles) and columns(time_steps)
filt_data = sio.loadmat('../HR_manometry_filtData/KH_filtData.mat')
# load a subset if required
data_in = filt_data['filtData']

#detect the Haps and Non-Haps as labels 2 and 1 respectively in a matrix of
#same dimension as input dataset
detector = HapsNonHapsDetector(data_in)
data_label = detector.obtainHapsNonHapsLabel()

# Plot the detected events. Note: it does contain false orphaned marks. Should be called
# after obtainHapsNonHapsLabel() method
detector.showHapsNonHaps()

# Here, the events are clustered and orphaned marks are removed. If the cluster
# has less than 3 events, delete those as events
cluster_mat = ClusterEvents(data_label).getClusteredEventsAsMatrix()

# Plot the clustered events with each label marked as a random colour

def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

# divide the colour map into 100 segments and assign colour randomly to labels
cmap = get_cmap(100)
map_colour = {}
for val in np.nditer(np.unique(cluster_mat)):
    map_colour[int(val)] = cmap(random.randint(0, 100))

# plot the figure with the labels as different colour
plt.figure()
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
