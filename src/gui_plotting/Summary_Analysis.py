
"""
    Author: Shameer Sathar
    Description: Provide Summary Details
"""

import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter

import config_global as sp

class SummaryAnalysis():

    def __init__(self, cyclic, haps, signals) :
        wave_metrics = []
        wave_metrics, event_matrix_cyclic = self.characteriseWaves(cyclic, 0, signals, wave_metrics)
        wave_metrics, event_matrix_haps = self.characteriseWaves(haps, 1, signals, wave_metrics)
        self.plot_summary_window(wave_metrics, event_matrix_cyclic)
        #self.win.show()

    def characteriseWaves(self, waves, wave_type, signals, wave_metrics):
        #initilise all the variables storing the counts
        retrograde = 0
        antegrade =0
        idx = 0
        wave_class = {}
        event_matrix = np.zeros(signals.shape)
        for key in waves.keys()[1:]:
            array = waves[key]
            amplitudes = signals[array[:, 0], array[:, 1]]
            event_matrix[array[:, 0], array[:, 1]] = 1
            z = np.polyfit(array[:,0], array[:, 1], 1)
            f = np.poly1d(z)
            x_new = np.linspace(np.min(array[:, 0]), np.max(array[:, 0]), 10)
            y_new = f(x_new)

            # reject groups that are grouped for 3 channels or less
            if(np.max(array[:,0]) - np.min(array[:,0]) < 4):
                continue

            slope = (y_new[-1] - y_new[0])/(x_new[-1] - x_new[0])
            if (slope < 0):
                retrograde+=1
                wave_class[key] = 0
            elif (slope > 0):
                antegrade+=1
                wave_class[key] = 1
            else:
                # reject group that are Instantaneuous
                print('Instantaneuous wave detected and removed')
                continue
            wave_metrics.append([wave_type, np.average(amplitudes), wave_class[key], np.abs(1/slope), x_new[-1] - x_new[0]])
        print('Signal Type', wave_type,'# of Antegrade waves', antegrade, '# of Retrograde waves', retrograde)
        return wave_metrics, event_matrix

    def plot_summary_window(self, wave_metrics, event_matrix):
        df = pd.DataFrame(wave_metrics)
        df.columns = ['Wave Type', 'Amplitudes', 'Direction', 'Velocity', 'Length']
        df.loc[df['Velocity'] > 40, 'Velocity'] = 0
        fig = plt.figure()
        plt.subplot(231)
        ax1 = sns.boxplot(x="Wave Type", y="Amplitudes", hue='Direction', data=df,showfliers=False)
        ax1.set_xticklabels(['Cyclic', 'HAPS'], fontsize=10)
        #ax1.title('Amplitude variation for cyclic/HAPS grouped based on their direction')
        plt.subplot(232)
        ax2 = sns.boxplot(x="Wave Type", y="Length", hue='Direction', data=df, showfliers=False)
        ax2.set_xticklabels(['Cyclic', 'HAPS'], fontsize=10)

        plt.subplot(233)
        ax3 = sns.boxplot(x="Wave Type", y="Velocity", hue='Direction', data=df, showfliers=False)
        ax3.set_xticklabels(['Cyclic', 'HAPS'], fontsize=10)

        plt.subplot(234)
        ax4 = sns.regplot(x="Amplitudes", y="Velocity", data=df)

        if not (df.loc[df['Wave Type'] == 0]).empty:
            plt.subplot(235)
            ax5 = sns.regplot(x="Amplitudes", y="Velocity", data=df.loc[df['Wave Type'] == 0])
        if not (df.loc[df['Wave Type'] == 1]).empty:
            plt.subplot(236)
            ax6 = sns.regplot(x="Amplitudes", y="Velocity", data=df.loc[df['Wave Type'] == 1])

        fig2=plt.figure(figsize=(16, 12))
        print(np.max(event_matrix))
        rows, cols = event_matrix.shape
        frequency_matrix=np.zeros(event_matrix.shape)
        event_matrix[:, 0] = 1
        for row in range(0, rows):
            event_pos = np.where(event_matrix[row,:] > 0)
            diff_event_pos = np.diff(event_pos)
            # print("event_pos", event_pos)
            # print("Diff value is", diff_event_pos)
            index = 1
            for col in range(1, len(event_pos[0])):
                frequency_matrix[row,event_pos[0][col]-10: event_pos[0][col]+10] = diff_event_pos[0,col-1]
        frequency_matrix = gaussian_filter(frequency_matrix, [1, 3])
        ax = sns.heatmap(frequency_matrix, vmin=0, vmax=500, cmap='jet')
        plt.show()
