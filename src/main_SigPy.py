#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: Shameer Sathar
    Description: GUI for training and plotting the activation times.
"""

import os

# External dependencies
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import scipy.io as sio
import sys
import matplotlib
from matplotlib import pyplot as plt
# Internal dependencies
import config_global as sp
from gui_plotting.mpl_plots  import *
from gui_plotting.Gui_Main import GuiMain

import numpy as np
np.set_printoptions(linewidth=1000, precision=3, threshold=np.inf)


"""
Manometry Pressure Data
"""

sp.datFileName = '/media/hpc/codes/GitLab/event_analyser/utils/python_read_data/CM_20120414_ALL_markedData.mat'
sp.dat = sio.loadmat(sp.datFileName)['data']['sig'][0][0][1:50, 0:20000]
sp.sample_frequency = 1

# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__' :
    sp.app = QtGui.QApplication(sys.argv)
    sp.app.setApplicationName('ManoPy')

    # Run GUI
    sp.gui = GuiMain()
    sp.gui.show()

    """
    Create data here and add to the curve
    """
    # Set plot data
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
