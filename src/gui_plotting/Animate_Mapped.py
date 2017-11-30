import sys
import os
import numpy as np
import platform
import time
import threading
from threading import Thread


from multiprocessing import Process

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

import config_global as sp

class AnimateMapped():

    def __init__(self) :
        self.plot_amplitude_map()



    def btn_animation_set_play(self):

        #print("Setting play button")

        btnPlayIconPath = sp.graphicsPath + "btnPlayTiny.png"

        self.btnPlayPause.setIcon(QtGui.QIcon(btnPlayIconPath))
        try:
            self.btnPlayPause.clicked.disconnect()
        except Exception as e:
            print(e)

        self.btnPlayPause.clicked.connect(self.play_animation)



    def btn_animation_set_pause(self):

        #print("Setting pause button")

        self.btnPlayPause.setFixedHeight(20)
        self.btnPlayPause.setFixedWidth(20)

        btnPauseIconPath = sp.graphicsPath + "btnPauseTiny.png"

        self.btnPlayPause.setIcon(QtGui.QIcon(btnPauseIconPath))
        self.btnPlayPause.setIconSize(QtCore.QSize(20,20))

        try:
            self.btnPlayPause.clicked.disconnect()
        except Exception as e:
            print(e)

        self.btnPlayPause.clicked.connect(self.pause_animation)



    def play_animation(self):
        self.ampMap.Playing = True

        self.ampMap.play(self.ampMap.currentFrameRate)
        self.btn_animation_set_pause()
        self.playPauseUI_repaint()



    def pause_animation(self):
        self.ampMap.Playing = False

        self.ampMap.play(0)
        self.btn_animation_set_play()
        self.playPauseUI_repaint()



    def change_animation_data_to_chans(self) :

        self.datToAnimate= sp.dat['filtData']
        self.change_animation_data()
        self.playPauseUI_repaint()



    def change_animation_data_to_events(self) :
        if 'gridEventData' in sp.dat['SigPy'].keys() :
            self.datToAnimate = sp.dat['SigPy']['gridEventData']
            self.change_animation_data()
        else:
            pass
            # self.statBar.showMessage("First run 'Detect Slow-wave events'")



    def change_animation_data(self) :
        self.playPauseUI_repaint()

        self.ampMap.priorIndex = self.ampMap.currentIndex
        self.ampMap.currentIndex = self.ampMap.priorIndex
        self.ampMap.setLevels(0.5, 1.0)



        self.ampMap.setImage(self.add_row_padding_to_grid_data(self.datToAnimate))

        self.play_animation()



    def change_frameRate(self, intVal):
        self.playPauseUI_repaint()

        self.ampMap.currentFrameRate = intVal
        fpsLabelStr = str(np.round((self.ampMap.currentFrameRate / self.ampMap.realFrameRate)[0],1)[0]) + " x"
        self.fpsLabel.setText(fpsLabelStr)

        if self.ampMap.Playing == True :
            self.ampMap.play(self.ampMap.currentFrameRate)

        self.playPauseUI_repaint()


    def playPauseUI_repaint(self):
        self.btnPlayPause.repaint()
        self.speedSlider.repaint()
        self.LayoutWidgetPlayPauseSpeed.repaint()
        self.fpsLabel.repaint()

        self.btnAmplitude.repaint()
        self.btnCNNEvents.repaint()



    def add_row_padding_to_grid_data(self,datToAnimate):
        padH = 1
        datToAnimateShape = datToAnimate.shape[0], datToAnimate.shape[1], datToAnimate.shape[2] + padH
        paddedDatToAnimate = np.ones(shape=datToAnimateShape)
        paddedDatToAnimate[:, :, padH : paddedDatToAnimate.shape[2]] = datToAnimate
        return paddedDatToAnimate



    def plot_amplitude_map(self):

        # Create animation window
        self.ampMap = pg.ImageView()
        print(self.ampMap.view.state['limits'])
        self.ampMap.view.setLimits(xMin=0, xMax=16, yMin=0, yMax=16, minXRange=0, maxXRange=16, minYRange=0, maxYRange=16)
        print(self.ampMap.view.state['limits'])

        # allowed = ['xMin', 'xMax', 'yMin', 'yMax', 'minXRange', 'maxXRange', 'minYRange', 'maxYRange']

        self.ampMap.setWindowTitle("Mapped Animating")

        # Preload data

        sp.dat['SigPy']['gridChannelData'] = map_channel_data_to_grid()

        if 'toaIndx' not in sp.dat['SigPy'] :
            print("Note! To plot CNN SW event data, please first run Detect Slow-Wave Events.")
            # self.ampMap.showMessage("Note! To plot CNN SW event data, please first run Detect Slow-Wave Events.")
        else:
            sp.dat['SigPy']['gridEventData'] = map_event_data_to_grid_with_trailing_edge()

        gridDataToAnimate = sp.dat['SigPy']['gridChannelData']


        self.ampMap.setImage(self.add_row_padding_to_grid_data(gridDataToAnimate))
        self.ampMap.show()

        ## ======= TOP NAV ===========
        ## -- Play pause speed controls
        # Set default animation speed to sampling frequency fps

        self.ampMap.singleStepVal = np.round((sp.dat['SigPy']['sampleRate'] / 2)[0], 1)

        self.ampMap.currentFrameRate = sp.dat['SigPy']['sampleRate']
        self.ampMap.realFrameRate = sp.dat['SigPy']['sampleRate']
        self.ampMap.currentFrameRate = self.ampMap.realFrameRate * 2 # Start at double speed

        # Create play pause speed controls
        self.btnPlayPause = QtGui.QPushButton('')
        self.btn_animation_set_pause()

        self.speedSlider = QtGui.QSlider()
        self.speedSlider.setOrientation(QtCore.Qt.Horizontal)
        self.speedSlider.setMinimum(0)
        self.speedSlider.setMaximum(self.ampMap.singleStepVal * 16)
        self.speedSlider.setValue(self.ampMap.currentFrameRate)


        self.speedSlider.setSingleStep(self.ampMap.singleStepVal)

        self.speedSlider.valueChanged.connect(self.change_frameRate)

        fpsLabelStr = str(np.round((self.ampMap.currentFrameRate / self.ampMap.realFrameRate)[0],1)[0]) + " x"
        self.fpsLabel = QtGui.QLabel(fpsLabelStr)


        ## -- Data select -- live / events / amplitude
        self.radioGrpAnimationData = QtGui.QButtonGroup()

        self.btnAmplitude = QtGui.QRadioButton('Amplitude')
        self.btnCNNEvents = QtGui.QRadioButton('CNN Events')
        self.btnLive = QtGui.QRadioButton('Live')


        self.btnAmplitude.clicked.connect(self.change_animation_data_to_chans)
        self.btnCNNEvents.clicked.connect(self.change_animation_data_to_events)

        self.btnAmplitude.setChecked(1);

        self.radioGrpAnimationData.addButton(self.btnAmplitude, 0)
        self.radioGrpAnimationData.addButton(self.btnCNNEvents, 1)

        self.radioGrpAnimationData.setExclusive(True)

        ## -- Add toolbar widgets to a proxy container widget
        self.LayoutWidgetPlayPauseSpeed = QtGui.QWidget()
        self.qGridLayout = QtGui.QGridLayout()

        # self.qGridLayout.setRowMinimumHeight(0, 50)

        self.qGridLayout.setHorizontalSpacing(14)

        self.qGridLayout.setContentsMargins(8,0,8,0)

        self.qGridLayout.addWidget(self.btnPlayPause, 0,0)
        self.qGridLayout.addWidget(self.speedSlider, 0,1)
        self.qGridLayout.addWidget(self.fpsLabel, 0,2)

        self.qGridLayout.addWidget(self.btnAmplitude, 0,3)
        self.qGridLayout.addWidget(self.btnCNNEvents, 0,4)

        self.LayoutWidgetPlayPauseSpeed.setLayout(self.qGridLayout)

        self.proxyWidget = QtGui.QGraphicsProxyWidget()
        self.proxyWidget.setWidget(self.LayoutWidgetPlayPauseSpeed)
        self.proxyWidget.setPos(0, 0)

        print("self.ampMap.ui: ", self.ampMap.ui)

        self.ampMap.scene.addItem(self.proxyWidget)

        # Automatically start animation
        self.play_animation()
