"""
    Author: Shameer Sathar
    Description: A module of functions for easy configuration.
"""

import os
import numpy as np
import scipy.io as sio

datFileName = '../CM_filt_raw_data.mat'

dat = sio.loadmat(datFileName)
sample_frequency = 1
