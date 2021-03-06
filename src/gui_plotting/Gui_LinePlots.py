""" Standard imports """

"""
    Author: Shameer Sathar
    Description: Provide Gui Interface.
"""
import sys
import os
import numpy as np
import platform
import time

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, USE_PYSIDE
from pyqtgraph.dockarea import *

# User defined imports
import config_global as sp
import random
import matplotlib.pyplot as plt
from random import shuffle
# from TrainingDataPlot import TrainingDataPlot

class GuiLinePlots:

    def __init__(self):
        """
        Initialise the properties of the GUI. This part of the code sets the docks, sizes
        :return: NULL
        """

        self.set_current_dataset()

        self.plotsScroll = pg.PlotWidget(title="Pressure Waves Line Graphs")
        self.plotsZoomed = pg.PlotWidget(title="Zoomed-in Line Graphs")
        self.set_rect_region_ROI()

        self.add_scatter_plots()
        self.set_crosshair()
        self.elec = []

        self.refresh_plots()

        # self.trainingDataPlot = TrainingDataPlot()


    def refresh_plots(self):
        self.clear_plots()
        self.set_current_dataset()
        self.set_plot_data()



    def set_current_dataset(self) :

        # Set initial plot data
        self.plotData = sp.dat
        self.nChans = self.plotData.shape[0]
        self.nSamples = self.plotData.shape[1]
        self.timeBetweenSamples = sp.sample_frequency
        self.timeStart = 0
        self.isNormal = True


    def clear_plots(self):
        self.curves_left = []
        self.curves_right = []
        self.curve_bottom = []
        self.elec = []
        self.plotData = []
        self.curves_left = []
        self.curves_right = []
        self.curve_bottom = []
        self.markersSWs = []


    def add_scatter_plots(self):

        self.clear_plots()

        c = pg.PlotCurveItem(pen=pg.mkPen('r', width=2))
        c_event = pg.PlotCurveItem(pen=pg.mkPen('r', width=2))
        self.curve_bottom.append(c)
        self.curve_bottom.append(c_event)

        self.plotsScroll.setYRange(0, 7600)
        self.plotsScroll.setXRange(0, 30000)

        for i in range(self.nChans):

            c1 = pg.PlotCurveItem(pen=('k'))
            c1.setPos(0, i)
            self.curves_left.append(c1)
            self.plotsScroll.addItem(c1)

            c2 = pg.PlotCurveItem(pen=('k'))
            c2.setPos(0, i)
            self.curves_right.append(c2)
            self.plotsZoomed.addItem(c2)


        self.swMarksScrlPlot = pg.ScatterPlotItem(size=8, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 160))
        self.swMarksZoomPlot = pg.ScatterPlotItem(size=8, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 160))
        self.plotsScroll.addItem(self.swMarksScrlPlot)
        self.plotsZoomed.addItem(self.swMarksZoomPlot)


        self.proxy = pg.SignalProxy(self.plotsZoomed.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.plotsZoomed.scene().sigMouseClicked.connect(self.onClick)
        self.plotsZoomed.sigXRangeChanged.connect(self.updateRegion)
        self.plotsZoomed.sigYRangeChanged.connect(self.updateRegion)


    def set_crosshair(self):
        """
        Cross hair definition and initiation
        """
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.plotsZoomed.addItem(self.vLine, ignoreBounds=True)
        self.plotsZoomed.addItem(self.hLine, ignoreBounds=True)



    def set_rect_region_ROI(self):
        '''
        Rectangular selection region
        '''
        self.rect = pg.RectROI([300, 300], [4000, 2000], pen=pg.mkPen(color='r', width=3))
        self.plotsScroll.addItem(self.rect)
        self.rect.sigRegionChanged.connect(self.update_plot)



    def set_curve_item(self):
        self.plotsScroll.setYRange(0, 7600)
        self.plotsScroll.setXRange(0, 30000)

        for i in range(self.nChans):
            c1 = pg.PlotCurveItem(pen=('k'))
            self.plotsScroll.addItem(c1)
            c1.setPos(0, i * 100)
            self.curves_left.append(c1)

            self.plotsScroll.resize(600, 10)

            c2 = pg.PlotCurveItem(pen=('k'))
            self.plotsZoomed.addItem(c2)
            c2.setPos(0, i * 100)
            self.curves_right.append(c2)
            self.plotsZoomed.showGrid(x=True, y=True)
            self.plotsZoomed.resize(600, 10)

        self.update_plot()



    def set_plot_data(self):
        # self.trainingDataPlot.set_plot_data(data)
        self.set_curve_item()

        for i in range(self.nChans):
            self.curves_left[i].setData(self.plotData[i])
            self.curves_right[i].setData(self.plotData[i])

        self.plotsScroll.setYRange(0, 7600)

        xAxisMax = np.min([self.nSamples, 50000])
        self.plotsScroll.setXRange(0, xAxisMax)

        ax = self.plotsScroll.getAxis('bottom')    #This is the trick

        tickInterval = int(xAxisMax / 6) # Produce 6 tick labels per scroll window

        tickRange = range(0, self.nSamples, tickInterval)

        # Convert indices to time for ticks -- multiply indices by time between samples and add original starting time.
        tickLabels = [str(self.timeBetweenSamples * tick + self.timeStart) for tick in tickRange]

        ticks = [list(zip(tickRange, tickLabels))]
        #print(ticks)

        ax.setTicks(ticks)


    def update_plot(self):

        xpos = self.rect.pos()[0]
        ypos = self.rect.pos()[1]
        width = self.rect.size()[0]
        height = self.rect.size()[1]
        self.plotsZoomed.setXRange(xpos, xpos+width, padding=0)
        self.plotsZoomed.setYRange(ypos, ypos+height, padding=0)


    def updateRegion(self):

        xpos = self.plotsZoomed.getViewBox().viewRange()[0][0]
        ypos = self.plotsZoomed.getViewBox().viewRange()[1][0]
        self.rect.setPos([xpos, ypos], update=False)


    def mouseMoved(self, evt):

        pos = evt[0]
        vb = self.plotsZoomed.plotItem.vb
        if self.plotsZoomed.sceneBoundingRect().contains(pos):
            mousePoint = vb.mapSceneToView(pos)
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())


    def onClick(self, evt):

        pos = evt.scenePos()
        vb = self.plotsZoomed.plotItem.vb
        if self.plotsZoomed.sceneBoundingRect().contains(pos):
            mousePoint = vb.mapSceneToView(pos)
            self.elec.append([int(round(mousePoint.y()/1.2)), int(round(mousePoint.x()))])
            self.trainingDataPlot.add_region([int(round(mousePoint.y()/1.2)), int(round(mousePoint.x()))])


    def mark_events(self, swPredictions, core_samples_mask, labels, wave_type) :
        # Convert predictions from NN to events to plot

        #import scipy.io as sio
        #sio.savemat(str(sp.datFileName.split('/')[-1].split('.')[:-1][0]) + 'analysed_data_' + str(wave_type) + '.mat', {'marks': swPredictions, 'mask': core_samples_mask, 'labels': labels})

        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        print('Estimated number of clusters: %d' % n_clusters_)
        scatter_points = np.where(swPredictions == wave_type)
        X = np.array(scatter_points).transpose()
        # Black removed and is used for noise instead.
        unique_labels = set(labels)
        colors = [plt.cm.Spectral(each)
                  for each in np.linspace(0, 1, len(unique_labels))]
        shuffle(colors)
        symbols = ['none','o', 't']
        clustered_waves = {}
        idx = 0
        for k, col in zip(unique_labels, colors):
            col = col
            if k == -1:
                # Black used for noise.
                col = [0, 0, 0, 1]
                continue
            col = [val * 255 for val in col]
            color_sel = tuple(col);
            if wave_type == 2:
                color_sel = 'b'

            class_member_mask = (labels == k)

            xy = X[class_member_mask]
            self.swMarksScrlPlot.addPoints(xy[:, 1], xy[:, 0] * 100, symbol=symbols[wave_type], pen=pg.mkPen(None), brush=pg.mkBrush(color_sel), size=14*wave_type)
            self.swMarksZoomPlot.addPoints(xy[:, 1], xy[:, 0] * 100, symbol=symbols[wave_type], pen=pg.mkPen(None), brush=pg.mkBrush(color_sel), size=14*wave_type)
            if(xy.size):
                clustered_waves[idx] = np.array(xy)
                idx+=1
        return clustered_waves
