"""
    Author: Shameer Sathar
    Description: A module of functions for easy configuration.
"""

import os
import numpy as np
import scipy.io as sio

datFileName = '../HR_manometry_filtData/KH_filtData.mat'

dat = sio.loadmat(datFileName)
sample_frequency = 1
