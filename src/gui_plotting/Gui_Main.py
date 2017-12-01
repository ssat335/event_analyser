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

from HapsNonHapsDetector import HapsNonHapsDetector
from ClusterEvents import ClusterEvents
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
        self.amplitudeMapping = QtGui.QPushButton('Amplitude and Event Mapping')

        self.btnFindSWEvents.clicked.connect(lambda: self.detect_haps_non_haps_events())
        self.amplitudeMapping.clicked.connect(lambda: self.plot_amplitude_map())

        self.ctrlsLayout.addWidget(self.dataTypeLabel, row=self.add_one(), col=0)
        self.ctrlsLayout.addWidget(self.btnFindSWEvents, row=self.add_one(), col=0)
        self.ctrlsLayout.addWidget(self.amplitudeMapping, row=self.add_one(), col=0)

    # ==== EVENTS ====

    def detect_haps_non_haps_events(self):

        print("In detect events")
        self.statBar.showMessage("Detecting Events. . .")

        # Setup data and params
        self.dataForMarking = sp.dat['filtData']

        #detect the Haps and Non-Haps as labels 2 and 1 respectively in a matrix of
        #same dimension as input dataset
        detector = HapsNonHapsDetector(self.dataForMarking)
        data_label = detector.obtainHapsNonHapsLabel()
        clustered_labels = ClusterEvents(data_label).getClusteredEventsAsMatrix()

        self.LinePlots.mark_events(data_label, clustered_labels)

        # Output (logging and for user)
        print "Plotting done"
        # Output number of events marked (note this number may differ from the CNN n of predictions)
        statBarMessage = " Events marked "
        self.statBar.showMessage(statBarMessage)

    def plot_amplitude_map(self):
        pass
        #self.animatedMap = AnimateMapped()

    def setup_file_menu_triggers(self):
        self.ui.ui_menubar.quitAction.triggered.connect(lambda: self.exit_app())

    def exit_app(self) :
        self.close()
        sys.exit()

    def add_one(self):
        self.ctrlsRow+=1
        return self.ctrlsRow
