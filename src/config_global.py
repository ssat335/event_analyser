"""
    Author: Shameer Sathar
    Description: A module of functions for easy configuration.
"""

import os
import numpy as np
import scipy.io as sio

datFileName = '/home/ssat335/Desktop/event_analyser/utils/python_read_data/CM_20120414_ALL_markedData.mat'

dat = sio.loadmat(datFileName)['data']['sig'][0][0]
sample_frequency = 1
