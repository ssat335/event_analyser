
"""Clusters marked events based on neighbour channels and events occuring"""

import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
from collections import Counter
import random

__author__ = "Shameer Sathar, https://github.com/ssat335"
__version__ = "0.0.1"

class ClusterEvents:
    def __init__(self, marks):
        """
        Init function accepting data matrix as input.
        Args:
            marks: Numpy matrix of rows of channels and columns with each index labelled
        """
        self.data_marks = marks
        (self.channels, self.time_steps) = self.data_marks.shape
        self.search_zone_two_steps = 20
        self.search_zone_one_step = 10
        self.cluster_limit = 3
        self.data_image_cluster = np.zeros((self.channels, self.time_steps))

    def getClusteredEventsAsMatrix(self, label = 1):
        """
        Function converts the dictionary to matrix format.
        Args:
            label = Event label to be clustered
        Returns:
            Cleaned events without any orphas as a matrix with dimensions same
            as marks matrix received as input.
        """
        self.cluster = self.clusterEventsOnLabels(label)
        for key in self.cluster:
            self.data_image_cluster[key[1], key[0]] = self.cluster[key]
        return self.data_image_cluster

    def removeOrphans(self, channel_list):
        """
        Function removes all orphans which as clustered but the count is less than self.cluster_limit
        Args:
            channel_list = Event label with corresponding cluster label
        Returns:
            Cleaned events without any orphas as a dictionary:
            {(time_steps, channel): cluster_label}
        """
        count_of_cluster = Counter(channel_list.values())
        for key in count_of_cluster:
            value = count_of_cluster[key]
            if value < self.cluster_limit:
                channel_list = { k:v for k, v in channel_list.items() if v is not key}
        return channel_list

    def clusterEventsOnLabels(self, label = 1):
        """
        Function clusters events and returns each event label with corresponding cluster label.
        Args:
            label = Label informatoion to be clustered
        Returns:
            Each event label with corresponding cluster label as a dictionary as:
            {(time_steps, channel): cluster_label}
        """
        mat_column_sum = np.sum(self.data_marks, axis=0)
        non_zero_indexes = np.where(mat_column_sum > 0)[0]

        cluster_num = 0
        channel_list = {}
        existing_cluster_number = 0
        search_zone_upper = self.search_zone_two_steps
        search_zone_lower = self.search_zone_one_step

        for index in non_zero_indexes:
            channels_current = np.where(self.data_marks[:, index])[0].tolist()
            for channel in channels_current:
                found = False
                for key in channel_list:
                    if found is False:
                        if (index, channel) == key:
                            cluster_num = channel_list[(index, channel)]
                            found=True
                        else:
                            found=False
                if not found:
                    cluster_num = cluster_num + 1

                #print index, channel, cluster_num
                channel_list[(index, channel)] = cluster_num
                if channel - 2 >= 0:
                    idxes = np.where(self.data_marks[channel - 2, index-search_zone_upper:index+search_zone_upper] == label)[0]
                    if idxes.size:
                        for idx in range(0, idxes.size):
                            if (idxes[idx] + index-search_zone_upper, channel-2) in channel_list:
                                found = True
                                existing_cluster_number = channel_list[(idxes[idx] + index-search_zone_upper, channel-2)]
                            channel_list[(idxes[idx] + index-search_zone_upper, channel-2)] = cluster_num
                            #print 'Entry: ', idxes[idx] + index-search_zone_upper, channel-2
                if channel - 1 >= 0:
                    idxes = np.where(self.data_marks[channel - 1, index-search_zone_lower:index+search_zone_lower] == label)[0]
                    if idxes.size:
                        for idx in range(0, idxes.size):
                            if (idxes[idx] +  index-search_zone_lower, channel-1) in channel_list:
                                found = True
                                existing_cluster_number = channel_list[(idxes[idx] +  index-search_zone_lower, channel-1)]
                            channel_list[(idxes[idx] +  index-search_zone_lower, channel-1)] = cluster_num
                            #print 'Entry: ', idxes[idx] +  index-search_zone_lower, channel-1

                if channel + 1 < self.channels:
                    idxes = np.where(self.data_marks[channel + 1, index-search_zone_lower:index+search_zone_lower] == label)[0]
                    if idxes.size:
                        for idx in range(0, idxes.size):
                            if (idxes[idx] +  index-search_zone_lower, channel+1) in channel_list:
                                found = True
                                existing_cluster_number = channel_list[(idxes[idx] +  index-search_zone_lower, channel+1)]
                            channel_list[(idxes[idx] +  index-search_zone_lower, channel+1)] = cluster_num

                if channel + 2 < self.channels:
                    idxes = np.where(self.data_marks[channel + 2, index-search_zone_upper:index+search_zone_upper] == label)[0]
                    if idxes.size:
                        for idx in range(0, idxes.size):
                            if (idxes[idx] + index-search_zone_upper, channel+2) in channel_list:
                                found = True
                                existing_cluster_number = channel_list[(idxes[idx] + index-search_zone_upper, channel+2)]
                            channel_list[(idxes[idx] + index-search_zone_upper, channel+2)] = cluster_num

                if found:
                    for key, value in channel_list.items():
                        if value == cluster_num:
                            channel_list[key] = existing_cluster_number
        return self.removeOrphans(channel_list)
