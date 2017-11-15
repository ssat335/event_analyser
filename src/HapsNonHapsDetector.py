import matplotlib.pyplot as plt
import numpy as np
from detect_peaks import detect_peaks

class HapsNonHapsDetector:
    def __init__(self, data_mat_in):
        self.data = data_mat_in
        (self.channels, self.time_steps) = self.data.shape
        self.label_image = np.zeros((self.channels, self.time_steps))
        self.NonHapsLabel = 1
        self.HapsLabel = 2
        self.HapsWidth = 100

    def obtainHapsNonHapsLabel(self):
        for channel in range(0, self.channels):
            self.label_image[channel, self.detectNonHaps(self.data[channel, :])] = self.NonHapsLabel
            HapsIndexes = self.detectHaps(self.data[channel, :])
            for idx in HapsIndexes:
                self.label_image[channel, idx - self.HapsWidth: idx + self.HapsWidth] = 0
            self.label_image[channel, HapsIndexes] = self.HapsLabel
        return self.label_image

    def detectHaps(self, in_channel, mph_val = 80, mpd_val = 100):
        indexes = detect_peaks(in_channel, mph=mph_val, mpd=mpd_val, show=False)
        return indexes

    def detectNonHaps(self, in_channel, mph_val =20, mpd_val = 50):
        indexes = detect_peaks(in_channel, mph=mph_val, mpd=mpd_val, show=False)
        return indexes

    def showHapsNonHaps(self):
        self.obtainHapsNonHapsLabel()
        horizontal_spacing = 100
        for channel in range(0, self.channels):
            plt.plot(self.data[channel, :] + horizontal_spacing * channel, c='gray' )
            indexes = np.where(self.label_image[channel, :] == self.HapsLabel)
            plt.plot(indexes, self.data[channel, indexes] + horizontal_spacing * channel, '+', mfc=None, mec='b', lw=3)
            indexes = np.where(self.label_image[channel, :] == self.NonHapsLabel)
            plt.plot(indexes, self.data[channel, indexes] + horizontal_spacing * channel, '+', mfc=None, mec='r')
