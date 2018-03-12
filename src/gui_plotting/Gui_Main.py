""" Standard imports """

"""
    Author: Shameer Sathar
    Description: Provide Gui Interface.
"""
import sys
import os
import numpy as np
import platform

import sys
sys.path.append('..')

from multiprocessing import Process

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, USE_PYSIDE
from pyqtgraph.dockarea import *


import pickle
import matplotlib as mpl

mpl.use('TkAgg') # compatibility for mac
import matplotlib.pyplot as plt

# Locally-developed modules
import config_global as sp

from gui_plotting.Gui_Window import GuiWindow
from gui_plotting.Gui_LinePlots import GuiLinePlots
from gui_plotting.Summary_Analysis import SummaryAnalysis

from HapsNonHapsDetector import HapsNonHapsDetector
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt

class GuiMain(QtGui.QMainWindow):

    def __init__(self, parent=None):

        """
        Initialise the properties of the GUI, setup docks, controls and plots
        :return: NULL
        """
        super(GuiMain, self).__init__(parent)
        self.ui = GuiWindow()
        self.ui.setupUi(self)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        # Add menu, status bar, controls and plots
        self.add_menu_controls_and_plots()

        # Set filemenu
        self.setup_file_menu_triggers()

        self.setCentralWidget(self.area)

        self.setWindowTitle('SigPy')
        self.showMaximized()



    def add_menu_controls_and_plots(self) :

        # Add menu bar
        self.mbar = self.setMenuBar(self.ui.ui_menubar.ui_menubar)

        # Add status bar
        self.statBar = self.statusBar()

        # Add dock
        self.area = DockArea()
        self.d_controls = Dock("Controls", size=(50, 200))
        self.area.addDock(self.d_controls, 'left')

        # Add controls
        self.add_controls()
        self.d_controls.addWidget(self.ctrlsLayout, row=1, colspan=1)

        # Add main plots
        self.reset_add_plots()


    def set_dataType_text(self):
        self.dataTypeLabel.setText("Manometry Data Selected")

    def reset_add_plots(self) :
        self.LinePlots = []
        self.LinePlots = GuiLinePlots()

        if hasattr(self, 'd_plots'):
            self.d_plots.close()
        self.d_plots = Dock("Plots", size=(500, 200))

        self.d_plots.addWidget(self.LinePlots.plotsScroll, row=0, col=0)
        self.d_plots.addWidget(self.LinePlots.plotsZoomed, row=0, col=1)
        self.area.addDock(self.d_plots, 'right')




    def add_controls(self) :

        self.ctrlsLayout = pg.LayoutWidget()
        self.ctrlsRow = 0

        self.dataTypeLabel = QtGui.QLabel("")
        self.dataTypeLabel.setAlignment(QtCore.Qt.AlignBottom)
        self.set_dataType_text()

        self.btnFindSWEvents = QtGui.QPushButton('Detect Haps and Non-Haps Events')
        self.summaryAnalysis = QtGui.QPushButton('Summary analysis')

        self.btnFindSWEvents.clicked.connect(lambda: self.detect_haps_non_haps_events())
        self.summaryAnalysis.clicked.connect(lambda: self.summary_analysis())

        self.ctrlsLayout.addWidget(self.dataTypeLabel, row=self.add_one(), col=0)
        self.ctrlsLayout.addWidget(self.btnFindSWEvents, row=self.add_one(), col=0)
        self.ctrlsLayout.addWidget(self.summaryAnalysis, row=self.add_one(), col=0)

    # ==== EVENTS ====

    def detect_haps_non_haps_events(self):

        print("In detect events")
        self.statBar.showMessage("Detecting Events. . .")

        # Setup data and params
        self.dataForMarking = sp.dat

        #detect the Haps and Non-Haps as labels 2 and 1 respectively in a matrix of
        #same dimension as input dataset
        detector = HapsNonHapsDetector(self.dataForMarking)
        data_label = detector.obtainHapsNonHapsLabel()
        scatter_points = np.where(data_label == 1)
        activation_points = np.array(scatter_points).transpose()
        activation_points[:, 0] = activation_points[:, 0] * 22
        # Compute DBSCAN
        db = DBSCAN(eps=50, min_samples=3).fit(activation_points)
        core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True
        labels = db.labels_
        self.clustered_cyclic = self.LinePlots.mark_events(data_label, core_samples_mask, labels, 1)

        scatter_points = np.where(data_label == 2)
        activation_points = np.array(scatter_points).transpose()
        activation_points[:, 0] = activation_points[:, 0] * 35
        # Compute DBSCAN
        db = DBSCAN(eps=100, min_samples=3).fit(activation_points)
        core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True
        labels = db.labels_
        self.clustered_haps = self.LinePlots.mark_events(data_label, core_samples_mask, labels, 2)

        # Output number of events marked (note this number may differ from the CNN n of predictions)
        statBarMessage = " Events marked "
        self.statBar.showMessage(statBarMessage)

    def summary_analysis(self):
        self.summaryWin = SummaryAnalysis(self.clustered_cyclic, self.clustered_haps, sp.dat)

    def setup_file_menu_triggers(self):
        self.ui.ui_menubar.quitAction.triggered.connect(lambda: self.exit_app())

    def exit_app(self) :
        self.close()
        sys.exit()

    def add_one(self):
        self.ctrlsRow+=1
        return self.ctrlsRow
